The Viper Command-line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Concept
^^^^^^^^^^^

After we define the tasks, actions, jobs etc. in the workspace,
we need a way to execute them. Dropping into a Python shell and
using the Python API is one way to do that. However, that might
not be the most preferred approach for everyone.

Viper provides a command-line interface through the ``viper``
command to interact with the Python API without dropping into
a Python shell.


Similarity Between the Python API and Command-line Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CLI interface closely follows the Python API. Each of the
subcommands with a colon (``:``) represents a method of a class or
object. When we run ``viper --help``, we can see the signature of
the methods/subcommands.

For example, the subcommand ``viper hosts:from-file`` represents the
class method :py:meth:`viper.Hosts.from_file`,

In the help menu the signature of this subcommand is defined as
``[Hosts]`` which means that it returns a text (JSON)
representation of a :py:class:`~viper.Hosts`, object which can be
passed (piped) to another subcommand that expects the same via
standard input.

On the other hand, the ``results:order-by`` has the signature
``[Results -> Results]``. The subcommand represents the method
:py:meth:`viper.Results.order_by` and the signature
``[Results -> Results]`` means that the subcommand expects the text
(JSON) representation of a
:py:class:`~viper.Results` object.


Example: Output Piping as Method Chaining
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    viper hosts:from-file("hosts.csv") \
            | viper hosts:task task.ping \
            | viper runners:run --max-workers 50 \
            | viper results:final \
            | viper results:order-by host.hostname host.ip \
            | viper results:to-file results.csv \
            | viper results:format "{host.hostname}: {stdout}"

In the above example, following things are happening:

- The ``hosts:from-file`` subcommand with signature
  ``[Hosts]`` returns the text representation of a :py:class:`~viper.Hosts` object.

- ``hosts:task`` reads the output of ``hosts:from-file`` from standard input
  as it has the signature of ``[Hosts -> Runners]`` and returns
  :py:class:`~viper.Runners`.

- Then the ``runners:run`` subcommand with signature ``[Runners -> Results]``
  reads the output of ``hosts:task`` from standard input and returns
  :py:class:`~viper.Results`.

- Finally ``results:format`` with signature ``[Results -> str]`` turns the
  :py:class:`~viper.Results` into a string which cannot be passed (piped) to any
  further subcommand.


The data flow diagram:

    ``hosts:from-file`` -> :py:class:`~viper.Hosts` | ``hosts:task`` -> :py:class:`~viper.Runners`
    | ``runners:run`` -> :py:class:`~viper.Results` | ``results:final`` -> :py:class:`~viper.Results`
    | ``results:order-by`` -> :py:class:`~viper.Results` | ``results:to-file`` ->
    :py:class:`~viper.Results` | ``results:format`` -> `str`

The above CLI example is equivalent to the following Python example:

.. code-block:: python

    from viper import Hosts
    import task

    print(
        Hosts.from_file("hosts.csv")
        .task(task.ping())
        .run(max_workers=50)
        .final()
        .order_by("host.hostname", "host.ip")
        .to_file("results.csv")
        .format("{host.hostname}: {stdout}")
    )

.. tip:: Refer to :doc:`getting_started` to see how ``task.ping`` and ``hosts.csv`` are written.


Defining Actions
^^^^^^^^^^^^^^^^

Actions are simple Python functions that can be invoked using the ``viper lets`` subcommand.

Example:

Define an action in ``action.py``:

.. code-block:: bash

    cat > action.py << EOF

.. code-block:: python

    def add_them(a, b):
        return int(a) + int(b)

.. code-block:: bash

    EOF

Now invoke the action:

.. code-block:: bash

    viper lets action.add_them 5 10

Output: ::

    15


Defining Viper Objects: Hosts, Task
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to actions, we can also define functions that return an instance of
:py:class:`~viper.Task` or :py:class:`~viper.Hosts`. The ``*:from-func``
subcommands will invoke the function to get the object it returns.

Example: Define a host group in ``hosts.py``

.. code-block:: bash

    cat > hosts.py << EOF

.. code-block:: python

    from viper import Hosts, Host

    def group1():
        return Hosts.from_items(
            Host("192.168.0.11", hostname="host11"),
            Host("192.168.0.12", hostname="host12"),
            Host("192.168.0.13", hostname="host13"),
            Host("192.168.0.14", hostname="host14"),
            Host("192.168.0.15", hostname="host15"),
        )

.. code-block:: bash

    EOF

Get the hosts count in terminal:

.. code-block:: bash

    viper hosts hosts.group1 | viper hosts:count

Output: ::

    5


.. note::

    ``viper hosts`` is an alias of ``viper hosts:from-func``.
    Similarly, ``viper task`` is an alias of ``viper task:from-func``.

    However, ``viper results`` is an alias of ``viper results:from-history``
    as there's no reason to write results ourselves. It should come from
    the database.

    So there's no ``results:from-func``, neither ``runners:from-func`` and so on.


.. tip::

    Refer to :doc:`getting_started` to find the example of task and job definitions.


Defining Utilities: Handlers, Filters, Sort Keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defining handlers, filters and sort keys are similar to
defining actions but the first argument of the defined function
is reserved for an instance of viper data type which
it receives from the standard input.

Example:

Define a general handler in ``handler.py`` that operates on
all :py:class:`~viper.collections.Items` instances:

.. code-block:: bash

    cat > handler.py << EOF

.. code-block:: python

    import sys

    def log_count(items, arg1):
        print(f"There are {items.count()} {arg1}.", file=sys.stderr)
        return items

.. code-block:: bash

    EOF

Use the handler:

.. code-block:: bash

    viper hosts hosts.group1 \
            | viper hosts:pipe handler.log_count hosts \
            | viper hosts:count

Output: ::

    There are 5 hosts.
    5


.. note:: Here ``arg1`` recieves the second argument passed to ``hosts:pipe``.


Similarly filters and sort keys can be defined using functions having
the first argument reserved for the object it will operate on, and the
subsequent arguments for the variables that will be passed while invoking
the ``*:filter`` and ``*:sort`` subcommands.

However, we hardly will need to really define filters and sort keys like this
as most of the requirements of sorting and filtering should be satisfied with
the ``*:order-by`` and ``*:where`` subcommands respectively.
