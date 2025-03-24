
import pytest

def test_example():
    assert 1 == 1

def test_math():
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
    assert isinstance(3.14, float)
    assert 5 in [1, 2, 3, 4, 5]


@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (2, 2, 4),
    (3, 5, 8)
])
def test_add(a, b, expected):
    assert a + b == expected
    
    
@pytest.fixture
def user_data():
    return {"name": "Alice", "age": 30}

def test_user_name(user_data):
    assert user_data["name"] == "Alice"

def test_user_age(user_data):
    assert user_data["age"] == 30

def divide(a, b):
    return a / b

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

class TestMath:
    def test_add(self):
        assert 1 + 1 == 2

    def test_mul(self):
        assert 2 * 3 == 6