from collections import namedtuple
from enum import Enum
import gettext
from pathlib import Path

import chardet


def set_i18n():
    # user application must use
    # gettext.bindtextdomain("exam2pdf", localedir=application_locales)
    trans = gettext.translation("exam2pdf", fallback=True)
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
    """Try to guess file encoding.

    Args:
        file_path: file you want to guess the encoding.

    Returns:
        The file encoding.

    Raises:
        Exam2pdfException: if the given file is not found
        and if chardet.detect["encoding"] is None.
    """
    try:
        result = chardet.detect(file_path.read_bytes())
    except FileNotFoundError:
        message = _("csv file not found: ") + str(file_path)
        raise Exam2pdfException(message)

    encoding = result["encoding"]

    if encoding is None:
        message = _("no encoding found for file ") + str(file_path)
        raise Exam2pdfException(message)

    return encoding
