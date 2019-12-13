"""Viper Actions Demo
~~~~~~~~~~~~~~~~~~~~~
A viper action is a plain Python function that viper executes when called.
An action takes optional arguments passed while invoking the command and can return
anything. If it returns ``None``, nothing will be printed to stdout. Otherwise the
string representation of the returned object will be printed.

If multiple objets are returned, they will be printed in separate lines.

Viper Action Definition Structure
---------------------------------

.. code-block:: python

    def action_name(*args: str) -> object:
        # Do something and return anything

You can run it with

.. code-block:: bash

    viper lets action_name
"""

from viper import Results

import typing as t


def get_triggers() -> t.Sequence[float]:
    """Get the unique trigger times from history"""

    results = Results.from_history(final=True).all()
    triggers = set(x.trigger_time for x in results)
    return tuple(sorted(triggers))
