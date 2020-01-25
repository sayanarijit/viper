The Viper Python API
~~~~~~~~~~~~~~~~~~~~~~~

The Concept
^^^^^^^^^^^

Viper provides a powerful collection of data types such as :py:class:`~viper.Hosts`,
:py:class:`~viper.Runners`, :py:class:`~viper.Results` etc. and uses *method chaining*
to perform different operations. The :py:mod:`viper.collection` module contains the
collection of such data types. These data types share some common properties as
all the data types inherit from the :py:class:`~viper.collections.Collection` class.

Example: Method Chaining
^^^^^^^^^^^^^^^^^^^^^^^^

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


Unit vs Container Types
^^^^^^^^^^^^^^^^^^^^^^^
The above mentioned data types can be categorised as unit and container types.
The unit ones inherit from the :py:class:`~viper.collections.Item` class, while the
container types inherit from :py:class:`~viper.collections.Items` class.

Below are the list of unit types and their container type counterparts:

=========================   ==========================
Unit Types                  Container Types
=========================   ==========================
:py:class:`~viper.Task`
:py:class:`~viper.Host`     :py:class:`~viper.Hosts`
:py:class:`~viper.Runner`   :py:class:`~viper.Runners`
:py:class:`~viper.Result`   :py:class:`~viper.Results`
=========================   ==========================


Useful Common Properties & Abilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The properties mentioned below are common to both unit and composite type objects.

- **Immutable:** All the datatypes are immutable i.e. they cannot be modified
  once initialized. This is to prevent any unexpected behaviour caused due to
  stateful-ness.

- **.from_json() and .to_json():** All the objects can be initialized from JSON
  texts using the ``.from_json()`` factory method and can be dumped back to JSON
  using the ``.to_json()`` method. This enables the objects to use a wide range of
  mediums such as the Unix pipes.

- **.format():** The objects can be converted to a custom formatted
  string using the ``.format()`` method. Example:
  ``host.format("{ip} {hostname} {meta.tag}")``


Useful Abilities Common to the Unit Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These abilities are common to :py:class:`~viper.Task`, :py:class:`~viper.Host`,
:py:class:`~viper.Runner` and :py:class:`~viper.Result` unit type objects.

- **.from_dict() and .to_dict():** Helps representing the objects as Python dictionaries.

Useful Abilities Common to the Container Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These abilities are common to :py:class:`~viper.Hosts`, :py:class:`~viper.Runners`
and :py:class:`~viper.Results` container type objects.

- **.from_items() and .to_items():** The ``.from_items()`` factory method is the
  recommended way to initialize container type objects. Although it can be a little slower,
  it removes duplicate items and performs other important checks before initializing
  the object. It supports sequences, generators, unit objects or all at once.

  .. attention::

    .. code-block:: python

        # Bad
        Hosts((host1, host2, host3))

        # Good
        Hosts.from_items(host1, host2, host3)

  The ``.to_items()`` or the alias ``.all()`` returns the tuple of unit items back.

  Example:

  .. code-block:: python

    Hosts.from_items(
        host1, host2                      # Unit objects
        [host3, host4],                   # Sequence of objects
        (host for host in list_of_hosts)  # Generator of objects
    ).to_items()


- **.from_file() and to_file():** Container type objects can be initialized from text
  files and dumped back to text files with certain formats (currently supported `json`,
  `yml` and `csv`) using these methods.

  Example:

  .. code-block:: python

      Hosts.from_file("hosts.json").to_file("hosts.csv")

- **.from_list() and .to_list():** Similar to unit types' ``.from_dict()`` and ``.to_dict()``
  but operates with list of dictionaries that represent the unit type objects.

- **.count():** Returns the count of items it holds.

- **.head() and .tail():** Returns an instance of the same container type object
  containing first or last n items (n defaults to 10).

  Example:

  .. code-block:: python

    # Get the set of last 5 items from the set of first 10 items.
    hosts.head(10).tail(5)

- **.range():** Similar to ``.head()`` or ``.tail()`` but enables us to define both the
  limits (similar to Python's ``list[i:j]`` indexing).

  Example:

  .. code-block:: python

    # Exclude the last item (similar to list[0:-1])
    hosts.range(0, -1)

- **.sort():** Similar to Python's ``list.sort()`` but returns a new instance instead of
  making changes to the existing object (which is impossible because of immutability).

  Example:

  .. code-block:: python

    # Reverse sort by IP, then by hostname
    hosts.sort(key=lambda host: [host.ip, host.hostname], reverse=True)

- **.order_by():** Similar to ``.sort()`` but expects the field names instead of a function.
  Inspired by SQL.

  Example:

  .. code-block:: python

    # Reverse sort by ip, then by hostname
    hosts.order_by("ip", "hostname", reverse=True)

- **.filter():** Similar to Python's ``filter()`` but returns an instance of the same
  container type object containing the filteres items.

  Example:

  .. code-block:: python

    # Filter hosts where hostname starts with "foo"
    hosts.filter(lambda host: host.hostname.startswith("foo"))

- **.where():** Similar to filter, but expects the and field name, condition
  and value instead of a function. Inspired by SQL.

  Example:

  .. code-block:: python

    # Filter hosts where hostname starts with "foo"
    hosts.where(
        "hostname", WhereConditions.startswith, ["foo"]
    )


More on Task: Command Factories, Output Processors, Callbacks and ...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The minimum requirements of defining a :py:class:`~viper.Task` requires is to define
the task name and the command factory. Optionally, we can also define the stdout and
stderr processors, and also the pre and post run callbacks.

The command factory expects a :py:class:`~viper.Host` object and return a tuple of
string.

Example:

.. code-block:: python

    def ping_command(host):
        return "ping", "-c", "1", host.ip

The stdout and stderr processors expect a string and return a string.

Example:

.. code-block:: python

    def strip_output(txt):
        return txt.strip()

The pre run callback expects a :py:class:`~viper.Runner` object and doesn't return
anything. While the post run callback expects a :py:class:`~viper.Result` object and
doesn't return anything either.

Example:

.. code-block:: python

    import sys

    def log_command_pre_run(runner):
        command = runner.task.command_factory(runner.host, *runner.args)
        print("Running command:", command, file=sys.stderr)

    def log_result_post_run(result):
        print("OK:" if result.ok() else "ERROR:", result.host.hostname, file=sys.stderr)


.. note:: Logs are be printed to `stderr` as `stdout` is for the JSON encoded
  :py:class:`~viper.Results` object.


.. attention::

    The arguments ``command_factory``, ``stdout_processor``, ``stderr_processor``,
    ``pre_run`` and ``post_run`` callbacks expect normal functions, not lambdas.

    .. code-block:: python

        # Bad
        def ping():
            return Task(
                name="Ping once",
                command_factory=lambda host: "ping", "-c", "1", host.ip,
                stdout_processor=lambda txt: txt.strip(),
                stderr_processor=lambda txt: txt.strip(),
                pre_run=lambda runner: print(runner.to_dict(), file=sys.stderr),
                post_run=lambda result: print(result.to_dict(), file=sys.stderr),
            )

        # Good
        def ping():
            return Task(
                name="Ping once",
                command_factory=ping_command,
                stdout_processor=strip_output,
                stderr_processor=strip_output,
                pre_run=log_command_pre_run,
                post_run=log_result_post_run,
            )

Apart from these, a :py:class:`~viper.Task` also optionally expects ``timeout``,
``retry`` and ``meta``.

- **timeout:** The execution will timeout after the specified seconds if timeout is
  defined.

  The countdown doesn't count the time spent on the pre and post run
  callbacks, neither the command factory invocation. It only counts time spent on
  executing the generated command.

- **retry:** It defaults to 0. If more than 0, The runner will re-invoke the
  :py:meth:`~viper.Runner.run` method with the updated retry value if the
  command execution fails. The results generated for these retries will be stored
  in DB and will be available in history. They will have the same ``trigger_time`` but
  different ``start`` and ``end`` times.

  However, if the failure is caused by any reason other than the actual command
  invocation, such as while invoking the command factory or output processors or
  pre/post run callbacks, a Python error will be raised which won't be stored in DB.
  If any such error occurs while running the task in batch, it will be ignored with
  the traceback printed on stderr.

- **meta:** It is the same as the ``meta`` field in :py:class:`~viper.Host`. It should
  be generated only using the :py:func:`viper.meta` function.

  .. attention::

      .. code-block:: python

        # Bad
        def ping():
            return Task(
                name="Ping once",
                command_factory=ping_command,
                meta={"tag": "foo"},
            )

        # Good
        def ping():
            return Task(
                name="Ping once",
                command_factory=ping_command,
                meta=meta(tag="foo")
            )
