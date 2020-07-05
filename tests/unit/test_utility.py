import pytest
from exam2pdf.utility import exception_printer, safe_int


def test_exception_printer0():
    output = exception_printer(ValueError("error"))
    expected = "ValueError: error"

    assert output == expected


@pytest.mark.parametrize("number, expected", [["1", 1], ["1.2", 0], ["1a", 0]])
def test_safe_int(number, expected):
    result = safe_int(number)

    assert result == expected
