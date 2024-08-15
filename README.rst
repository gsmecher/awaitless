Awaitless
=========

If you're writing network-oriented code in Python, you're probably looking at
an asynchronous framework of some kind. Let's say you're also writing code
that's intended to be used interactively in IPython or Jupyter notebooks.

(Why would you ever use async interactively in IPython/JupyterLab? There's a
longer screed associated with an earlier attempt `here
<https://github.com/gsmecher/tworoutine>`_.)

That's a drag, because async is irrelevant for interactive use -- except you
need to sprinkle "await" and "async" keywords in exactly the right places or it
doesn't work.

For example, let's pretend "release_kraken" is a complicated piece of async
machinery.  It might take arguments, interacts with the world, and might return
a value. Here's a placeholder definition:

.. code-block:: ipython

    >>> async def release_kraken():
    ...     import aiohttp, http
    ...     async with aiohttp.ClientSession() as cs:
    ...         resp = await cs.post('http://httpbin.org/post')
    ...         return resp.status == http.HTTPStatus.OK

Let's say you're calling :code:`release_kraken()` in an interactive ipython
session:

.. code-block:: ipython

    >>> release_kraken() # doctest: +SKIP
    Out[1]: <coroutine object release_kraken ...>

The kraken is not released - your function never actually executes. All you get
is a "RuntimeWarning: coroutine was never awaited" slap on the wrist.  You
forgot the "await":


.. code-block:: ipython

    >>> await release_kraken()
    Out[1]: True

That's ... better? I mean, it's now "correct" according to asyncio conventions,
and we're making use of ipython's autoawait magic, but there is *never* any
ambiguity about a coroutine at the top level of an interactive session. The
user wanted to run some code, and forcing them to slavishly type "await" every
time is so pedantic it's user-hostile.

Let's do better:

.. code-block:: ipython

    >>> %load_ext awaitless
    >>> release_kraken()
    Out[1]: ...<Task finished ... result=True>

What did that do?

* The async code ran to completion, even though we didn't await it (note the
  'finished' and 'result')

* The return value is now a Task, not a coroutine(). However, both coroutines
  and Tasks are awaitable, so the switcheroo is (largely) API compatible.

Why?

Yes, "await" is only 6 extra keys to hit, but it's distracting and unnecessary.
You could have the same discussion about print()ing the results in a REPL
rather than just displaying them -- and ipython cares enough about this to make
it configurable.  (Try :code:`get_ipython().ast_node_interactivity='all'` if
you're curious.)

I find myself returning to `this article
<https://yosefk.com/blog/i-cant-believe-im-praising-tcl.html>`_ every year or
so. The author says:

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

    awaitless$ pytest
