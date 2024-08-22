# Copyright (c) 2024 t0.technology, Inc.
#
# Distributed under the terms of the BSD license.  The full license is in the
# file LICENSE, distributed as part of this software.


def doctest_coroutine_with_normal_yield():
    """
    This code path is utterly vanilla and we just want to make sure we didn't
    wreck it.

    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"
    >>> await hello()
    Out[1]: 'Hello world'
    """


def doctest_coroutine_to_task_expr():
    """
    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"
    >>> hello()
    Out[1]: <Task finished ... result='Hello world'>
    """


def doctest_coroutine_to_task_assignment():
    """
    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"
    >>> x = hello()
    >>> x
    Out[1]: <Task finished ... result='Hello world'>
    """


def doctest_coroutine_multiply_awaited():
    """
    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"
    >>> x = hello()
    >>> await x
    Out[1]: 'Hello world'
    >>> x
    Out[1]: <Task finished ... result='Hello world'>
    """


def doctest_coroutine_inside_sync_function():
    """
    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"
    >>> def hello_wrapper(): hello()

    If awaitless operates inside hello_wrapper(), it'll be adding an "await"
    statement inside a synchronous function - which isn't allowed.

    >>> import warnings
    >>> with warnings.catch_warnings():
    ...     warnings.simplefilter("ignore")  # hello() never awaited
    ...     hello_wrapper()
    """


def doctest_coroutine_inside_async_function():
    """
    >>> %reload_ext awaitless
    >>> async def hello(): return "Hello world"

    For async code, we have the _ability_ to modify the AST and substitute
    coroutines for tasks, but we shouldn't. Doing so would make code execute
    differently in ipython cells compared to library code, and we'd like to be
    able to cut and paste back and forth.

    >>> import types
    >>> async def hello_wrapper():
    ...    x = hello()
    ...    assert isinstance(x, types.CoroutineType), f"x was a {type(x)}, not a coroutine!"
    ...    return await x
    >>> await hello_wrapper()
    Out[1]: 'Hello world'
    """


def doctest_exception_inside_async_function():
    """
    Awaitless makes trouble for ipython stack trace tooling because it alters
    the AST. This test just raises an exception and ensures it's correctly
    propagated, which is enough to kick the tires on the tooling but not enough
    to really tickle the bits that are broken.

    Specifically, ipython's stack trace printer gets angry when we hand it AST
    entries with lineno attributes beyond the range of the code it's trying to
    introspect. I could trigger a problem interactively that doesn't seem to
    work in the doctest framework.

    I'm leaving this test in as a failsafe and/or a reminder.
    >>> import pytest
    >>> %reload_ext awaitless
    >>> async def hello(): raise ZeroDivisionError("Oh no")
    >>> with pytest.raises(ZeroDivisionError):
    ...     hello()
    """


def doctest_lambda():
    """
    Lambdas aren't special-cased, but work anyways. It's subtle and worth
    understanding why (and testing!)

    >>> import asyncio
    >>> %reload_ext awaitless
    >>> x = lambda: asyncio.sleep(0)
    >>> x()
    Out[1]: <Task finished ... result=None>

    ...wait, what? OK - this worked. That's because the lambda doesn't contain
    Expr or Statement nodes, and therefore doesn't trigger AST modification
    that would insert an illegal await.

    The actual conversion from coroutine to task occurred in the last line,
    which was an Expr.
    """
