# Copyright (c) 2024 t0.technology, Inc.
#
# Distributed under the terms of the BSD license.  The full license is in the
# file LICENSE, distributed as part of this software.

import ast
import textwrap
import IPython


# Convert coroutines in assignments into tasks
class CoroutineTransformer(ast.NodeTransformer):

    def visit_Module(self, node):
        """
        Insert "import" statements that we'll need to use later
        """

        node.body.insert(
            0,
            ast.Import(
                names=[
                    ast.alias(name="inspect", asname="_awaitless_inspect"),
                    ast.alias(name="asyncio", asname="_awaitless_asyncio"),
                ]
            ),
        )
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Inhibit AST transformation when we bump into Function nodes

        This inhibition is mandatory, because our AST modifications insert
        "await" nodes that are syntactically illegal inside a synchronous
        function context.
        """

        # subtree walk is inhibited without generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        """
        Inhibit AST transformation inside AsyncFunctionDef nodes.

        This is a judgement call - we need to draw a boundary between "I'm in an
        interactive shell", where we do AST transformations, and "I'm in a
        codebase" where we don't.

        Because we are unable to do AST transformations on synchronous
        functions (see visit_FunctionDef above), and because writing functions
        seems like a "coding" and not an "interacting" activity, it seems
        reasonable to draw the boundary at function calls of both synchronous
        and asynchronous types.
        """

        return node

    def visit_Expr(self, node):
        """
        Rewrite Expr nodes
        """

        t = ast.parse(
            textwrap.dedent(
                """
                    _awaitless_ttemp = None
                    if _awaitless_inspect.iscoroutine(_awaitless_ttemp):
                        _awaitless_ttemp = _awaitless_asyncio.create_task(_awaitless_ttemp)
                        await _awaitless_ttemp
                    _awaitless_ttemp
                """
            )
        )

        t.body[0].value = node.value  # assign _awaitless_ttemp

        # Replace node and don't generic_visit its children
        return t.body

    def visit_Assign(self, node):
        """
        Rewrite Assign nodes
        """

        t = ast.parse(
            textwrap.dedent(
                """
                    _awaitless_ttemp = None
                    if _awaitless_inspect.iscoroutine(_awaitless_ttemp):
                        _awaitless_ttemp = _awaitless_asyncio.create_task(_awaitless_ttemp)
                        await _awaitless_ttemp
                    target = _awaitless_ttemp
                """
            )
        )

        t.body[0].value = node.value  # assign _awaitless_ttemp
        t.body[-1].targets = node.targets  # assign results

        # Replace node and don't generic_visit its children
        return t.body


def load_ipython_extension(ipython=None):
    if ipython is None:
        ipython = IPython.get_ipython()

    if ipython is None:
        raise RuntimeError("Can't install awaitless: no IPython session exists!")

    ipython.ast_transformers.append(CoroutineTransformer())

    # We've created an implicit eventloop dependency - ensure all cells are
    # executed in an async context
    ipython.should_run_async = lambda *a, **kw: True

    # There's a bug in stack_data that's exposed by ipython "ultratb" traceback
    # code.  Newer ipython has a workaround here:
    #
    #     https://github.com/ipython/ipython/pull/14286
    #
    # For ipython 8.20 and earlier, we monkey-patch in a backport.
    if IPython.version_info < (8, 21, 0):
        from IPython.core import ultratb

        @property
        def lines(self):
            from executing.executing import NotOneValueFound

            try:
                return self._sd.lines
            except NotOneValueFound:

                class Dummy:
                    lineno = 0
                    is_current = False

                    def render(self, *, pygmented):
                        return "<Error retrieving source code with stack_data see ipython/ipython#13598>"

                return [Dummy()]

        ultratb.FrameInfo.lines = lines
