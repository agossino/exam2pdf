import re
import logging
from typing import List
from collections import namedtuple
from enum import Enum

LOGNAME = "quest2pdf"
LOGGER = logging.getLogger(LOGNAME)


class Quest2pdfException(BaseException):
    pass


class ItemLevel(Enum):
    """top level text
       top level image
           sub level text
           sub level image

           sub level test

       top level image
           sub level text

           sub level image
    """

    top = 0
    sub = 1


Item = namedtuple("Item", ["item_level", "text", "image"])


def exception_printer(exception_instance: Exception) -> str:
    """Format an exception class and instance in string
    """
    pattern: str = r"\W+"
    exc_list: List[str] = re.split(pattern, str(exception_instance.__class__))
    try:
        return exc_list[2] + ": " + str(exception_instance)
    except IndexError:
        return str(exception_instance)


def safe_int(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return 0
