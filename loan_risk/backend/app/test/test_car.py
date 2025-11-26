import pytest

@pytest.fixture
def my_car() -> str:
    return "Toyota"

def test_my_car_toyota(my_car: str):
    assert my_car == "Toyota" # True

def test_my_car_honda(my_car: str):
    assert my_car == "Honda" # False
