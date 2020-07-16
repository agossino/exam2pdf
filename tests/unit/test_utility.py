import pytest
from exam2pdf.utility import safe_int


@pytest.mark.parametrize("number, expected", [["1", 1], ["1.2", 0], ["1a", 0]])
def test_safe_int(number, expected):
    result = safe_int(number)

    assert result == expected
