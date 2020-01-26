Extending the Command-line Interface (using ``viperfile.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Why and How
^^^^^^^^^^^

The viper CLI can easily be extended to include custom subcommands using
the :py:mod:`viper.project` module.

To do this, you have to create a file named ``viperfile.py`` in the root
of your workspace. This file will contain the definition(s) of one or multiple
projects. A project works like a namespace for all the custom subcommands under it.


Example: Defining a Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is how a project can be defined in ``viperfile.py``:

.. code-block:: python

    from viper.project import Project, arg

    foo = Project("foo")


The :py:func:`viper.project.arg` function helps defining the command-line
arguments a.k.a options or switches that the subcommand expects.

Let's define a subcommand ``@foo:group1`` that expects optional arguments
``--login_name`` and ``--identity_file`` with some default values
and returns the text representation of a :py:class:`viper.Hosts` object.


Example: Defining a subcommand for host group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from viper import Host, Hosts, meta

    @foo.hostgroup(
        args=[
            arg("-l", "--login_name", default="root"),
            arg("-i", "--identity_file", default="/root/.ssh/id_rsa.pub"),
        ]
    )
    def group1(args):
        return Hosts.from_items(
            Host(
                ip="192.168.0.11",
                hostname="host11"
                login_name="root",
                identity_file=args.identity_file,
                meta=meta(provider="aws"),
            ),
            Host(
                ip="192.168.0.12",
                hostname="host12",
                login_name="root",
                identity_file=args.identity_file,
                meta=meta(provider="aws"),
            )
        )

Now running ``viper -h`` in that workspace will show us ``@foo:group1  [Hosts]``,
and running ``viper @foo:group1 --help`` will list the arguments it's expecting
and their default values.

The subcommand can now be executed as below:

.. code-block:: bash

    # Use the default values
    viper @foo:group1

    # Specify the login name and identity file
    viper @foo:group1 -l user1 -i ~user1/.ssh/id_rsa.pub


.. note::

    All the custom subcommands are prefixed with ``@`` to separate them from the
    core viper subcommands. And the string following ``@`` acts like a namespace
    that separates the subcommands belonging from different projects in the same
    viperfile.
