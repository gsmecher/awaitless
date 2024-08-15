# Copyright (c) 2024 t0.technology, Inc.
#
# Distributed under the terms of the BSD license.  The full license is in the
# file LICENSE, distributed as part of this software.

import ast
import textwrap
import IPython


# Convert coroutines in assignments into tasks
class CoroutineTransformer(ast.NodeTransformer):
    inner_context = False

    def visit_Module(self, node):
        # import inspect, asyncio
        node.body.insert(
            0,
            ast.Import(
                names=[
                    ast.alias(name="inspect", asname=None),
                    ast.alias(name="asyncio", asname=None),
                ]
            ),
        )
        self.generic_visit(node)
        return node

    def _trigger_inner_context(self, node):
        old_inner_context = self.inner_context
        self.inner_context = True
        node = self.generic_visit(node)
        self.inner_context = old_inner_context
        return node

    # The following AST nodes trigger a shift to an "inner context", where AST
    # rewriting is disabled.
    visit_FunctionDef = _trigger_inner_context
    visit_AsyncFunctionDef = _trigger_inner_context

    # The following AST nodes are rewritten.
    def visit_Expr(self, node):
        if self.inner_context:
            return self.generic_visit(node)

        t = ast.parse(
            textwrap.dedent(
                """
                    _ttemp = None
                    if inspect.iscoroutine(_ttemp):
                        _ttemp = asyncio.create_task(_ttemp)
                        await _ttemp
                    _ttemp
                """
            )
        )

        t.body[0].value = node.value  # assign _ttemp

        return t.body

    def visit_Assign(self, node):
        if self.inner_context:
            return self.generic_visit(node)

        t = ast.parse(
            textwrap.dedent(
                """
                    _ttemp = None
                    if inspect.iscoroutine(_ttemp):
                        _ttemp = asyncio.create_task(_ttemp)
                        await _ttemp
                    target = _ttemp
                """
            )
        )

        t.body[0].value = node.value  # assign _ttemp
        t.body[-1].targets = node.targets  # assign results

        return t.body


def load_ipython_extension(ipython=None):
    if ipython is None:
        ipython = IPython.get_ipython()

    if ipython is None:
        raise RuntimeError("Can't install awaitless: no IPython session exists!")

    ipython.ast_transformers.append(CoroutineTransformer())
    ipython.should_run_async = (
        lambda *a, **kw: True
    )  # CoroutineTransformer creates implicit eventloop dependency