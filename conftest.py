# Copyright (c) 2024 t0.technology, Inc.
#
# Distributed under the terms of the BSD license.  The full license is in the
# file LICENSE, distributed as part of this software.


import pytest
import IPython
import doctest
import functools
import operator


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config.pluginmanager.register(DoctestRunner(), "ipythondoctestrunner")
    config.pluginmanager.unregister(name="doctest")


class DoctestRunner:
    def pytest_collect_file(self, file_path, parent):
        if file_path.suffix == ".py":
            return Module.from_parent(parent, path=file_path)

        if file_path.suffix == ".rst":
            return File.from_parent(parent, path=file_path)


class Module(pytest.Module):
    def collect(self):
        parser = doctest.DocTestParser()
        finder = doctest.DocTestFinder(parser=parser)
        for test in finder.find(self.obj):
            yield DoctestItem.from_parent(parent=self, name=test.name, test=test)


class File(pytest.File):
    def collect(self):
        parser = doctest.DocTestParser()
        test = parser.get_doctest(
            self.fspath.read_text("utf-8"), {}, str(self.fspath), str(self.fspath), 0
        )
        yield DoctestItem.from_parent(parent=self, name=test.name, test=test)


class DoctestItem(pytest.Item):
    def __init__(self, name, parent, test):
        super().__init__(name, parent)
        self.test = test

    def runtest(self):
        checker = doctest.OutputChecker()
        shell = IPython.InteractiveShell.instance()

        for example in self.test.examples:

            if doctest.SKIP in example.options:
                continue

            with IPython.utils.capture.capture_output() as captured:
                result = shell.run_cell(example.source)

                optionflags = functools.reduce(
                    operator.or_,
                    example.options,
                    doctest.REPORT_NDIFF | doctest.ELLIPSIS,
                )

                if result.error_in_exec:
                    raise result.error_in_exec

                want = example.want.strip()
                got = captured.stdout.strip() if captured.stdout else ""

                if not checker.check_output(want, got, optionflags):
                    raise AssertionError(f"Expected {want}, got {got}")
