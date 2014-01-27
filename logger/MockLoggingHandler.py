"""
.. module:: Onyx Mock of Logging Handler
   :platform: Linux
   :synopsis: Mock logger to get messages, and test coloured decorator for logger
   :copyright: (c) 2012-2013 by Ernesto Bossi.
   :license: BSD.

.. moduleauthor:: Ernesto Bossi <bossi.ernestog@gmail.com>
"""
import logging
from pyparsing import *

ESC = Literal('\x1b')
integer = Word(nums)
escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer, ';')) +
                    oneOf(list(alphas)))

nonAnsiString = lambda s: Suppress(escapeSeq).transformString(s)


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        level = nonAnsiString(record.levelname.lower())#remove color formatting and another non-ANSI characters
        self.messages[level].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': []
        }
