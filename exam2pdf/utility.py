import re
from typing import List
from collections import namedtuple
from enum import Enum
import gettext
from pathlib import Path


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
    return exc_list[2] + ": " + str(exception_instance)


def safe_int(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return 0


def set_i18n():
    this_script_path = Path(__file__)
    locales = this_script_path.parent / "locales"
    trans = gettext.translation("exam2pdf", localedir=str(locales), fallback=True)
    return trans.gettext
