Awaitless
=========

If you're writing network-oriented code in Python, you're probably looking at
an asynchronous framework of some kind. Let's say you're also writing code
that's intended to be used interactively in ipython.

That's a drag, because async is irrelevant for interactive use -- except you
need to sprinkle "await" and "async" keywords in exactly the right places or it
doesn't work.

For example, let's pretend "tremendously_async_function" is a complicated piece
of async machinery.  It takes arguments, interacts with the world, and returns
a value.  Here's a placeholder function:

.. code-block:: ipython

    >>> async def tremendously_async_function(x):
    ...     import aiohttp
    ...     async with aiohttp.ClientSession() as cs:
    ...         return await cs.get('https://news.ycombinator.com/')

Let's say you're calling tremendously_async_function() in an interactive
ipython session:

.. code-block:: ipython

    >>> tremendously_async_function(3600)  # doctest: +SKIP
    Out[1]: <coroutine object tremendously_async_function ...>

oops! You get a "RuntimeWarning: coroutine was never awaited" slap on the
wrist and the function never actually runs. You forgot the "await":

.. code-block:: ipython

    >>> await tremendously_async_function(1)
    Out[1]: ...<ClientResponse(https://news.ycombinator.com/) [200 OK]>...

That's ... better? I mean, it's now "correct" according to asyncio conventions,
and we're making use of ipython's "autoawait" magic, but there is *never* any
ambiguity about a coroutine at the top level of an interactive session. The
user wanted to run some code, and forcing them to slavishly type "await" every
time is so pedantic it's user-hostile.

Let's do better:

.. code-block:: ipython

    >>> %load_ext awaitless
    >>> tremendously_async_function(1)
    Out[1]: ...<Task finished ... result=...>

What did that do?

* The async code ran to completion, even though we didn't await it (note the
  'finished' and 'result')

* The return value is now a Task, not a coroutine(). However, both coroutines
  and Tasks are awaitable, so the switcheroo is (largely) compatible.

Why?

Yes, "await" is only 6 extra keys to hit, but it's distracting and unnecessary.
You could have the same discussion about print()ing the results in a REPL
rather than just displaying them -- and ipython cares enough about this to make
it configurable.  (Try :code:`get_ipython().ast_node_interactivity='all'` if
you're curious.)

I find myself returning to `this article
<https://yosefk.com/blog/i-cant-believe-im-praising-tcl.html>`_ every year or
so:


The author says:

    I ain't gonna mock Tcl-scriptable tools no more. I understand what made the
    authors choose Tcl, and no, it's not just a bad habit. On a level, they
    chose probably the best thing available today in terms of
    ease-of-programming/ease-of-use trade-off (assuming they bundle an
    interactive command shell). If I need to automate something related to
    those tools, I'll delve into it more happily than previously.

In short: languages designed for interactive use (tcl, bash, etc) make syntax
decisions that are different than languages that are designed for programming.
Interactive languages tend to prioritize "shallow" tasks like command
invocation at the expense of language composition (functions, classes,
modules). IPython is a reasonable compromise - but not when coroutines are
involved.

Testing
-------

Run the following:

.. code-block:: bash

    awaitless$ pytest README.rst test.py

Installation
------------

For now, you need to put awaitless.py somewhere handy. Then, in ipython,

.. code-block:: ipython

    >>> %load_ext awaitless                     # doctest: +SKIP
