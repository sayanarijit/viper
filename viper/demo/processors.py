"""Viper Demo Output Processors

This module contains example of output processors to be used in task definition.


.. tip:: See :py:class:`viper.collections.Task` and :py:class:`viper.demo.tasks.ping`.
"""


def text_stripper(txt: str) -> str:
    """This is a stdout/stderr processor that strips the given text.

    :param str txt: The text to be stripped
    :rtype: str
    """
    return txt.strip()
