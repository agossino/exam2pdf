from collections import namedtuple
from enum import Enum
import gettext
from pathlib import Path

import chardet


def set_i18n():
    this_script_path = Path(__file__)
    locales = this_script_path.parent / "locales"
    trans = gettext.translation("exam2pdf", localedir=str(locales), fallback=True)
    return trans


_ = set_i18n().gettext


class Exam2pdfException(Exception):
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


def safe_int(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return 0


def guess_encoding(file_path: Path) -> str:
    """Try to guess file encoding
    """
    result = chardet.detect(file_path.read_bytes())
    encoding = result["encoding"]

    if encoding is None:
        raise Exam2pdfException("No encoding found for file %s", file_path)

    return encoding
