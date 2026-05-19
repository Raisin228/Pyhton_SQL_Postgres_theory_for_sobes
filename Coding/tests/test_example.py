import pytest


def add(a, b):
    return a + b


def check_num(num):
    if not isinstance(num, int):
        raise Warning(f"invalid value {num}")


def test_math():
    assert add(2, 3) == 6, "Сумма должна быть верной!"


def test_list_diff():
    assert [1, 2, 3] == [1, 2, 4]


def test_str_diff():
    assert "hello\nworld" == "hello\nWorld"


def test_raises():
    with pytest.raises(ValueError, match=r"invalid value \d+"):
        check_num("12314")


@pytest.mark.parametrize(["a", "b", "expected"], [
    (1, 1, 2),
    (2, 5, 7),
    (-1, 1, 0),
], ids=["first", "second", "third"])
def test_add(a, b, expected):
    assert a + b == expected

@pytest.mark.parametrize("num1", [1, 2, 3])
@pytest.mark.parametrize("num2", [1, 2, 3])
def test_service(num1, num2):
    assert num1 + num2 == num1 + num2