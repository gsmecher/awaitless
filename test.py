# Copyright (c) 2024 t0.technology, Inc.
#
# Distributed under the terms of the BSD license.  The full license is in the
# file LICENSE, distributed as part of this software.


def doctest_coroutine_with_normal_yield():
    """
    This code path is utterly vanilla and we just want to make sure we didn't
    wreck it.

    >>> import awaitless, IPython
    >>> shell = IPython.InteractiveShell.instance()
    >>> awaitless.load_ipython_extension(shell)
    >>> async def hello(): return "Hello world"
    >>> await hello()
    Out[1]: 'Hello world'
    """


def doctest_coroutine_to_task_expr():
    """
    >>> import awaitless, IPython
    >>> shell = IPython.InteractiveShell.instance()
    >>> awaitless.load_ipython_extension(shell)
    >>> async def hello(): return "Hello world"
    >>> hello()
    Out[1]: <Task finished ... result='Hello world'>
    """


def doctest_coroutine_to_task_assignment():
    """
    >>> import awaitless, IPython
    >>> shell = IPython.InteractiveShell.instance()
    >>> awaitless.load_ipython_extension(shell)
    >>> async def hello(): return "Hello world"
    >>> x = hello()
    >>> x
    Out[1]: <Task finished ... result='Hello world'>
    """


def doctest_coroutine_multiply_awaited():
    """
    >>> import awaitless, IPython
    >>> shell = IPython.InteractiveShell.instance()
    >>> awaitless.load_ipython_extension(shell)
    >>> async def hello(): return "Hello world"
    >>> x = hello()
    >>> await x
    Out[1]: 'Hello world'
    >>> x
    Out[1]: <Task finished ... result='Hello world'>
    """
