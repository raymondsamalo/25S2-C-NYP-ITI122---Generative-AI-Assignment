"""Unit tests for CustomerAccountStatusService."""
import pytest
from app.db.db import SqliteDB, create_and_populate_db
from app.services.account_status import CustomerAccountStatusService


@pytest.fixture(scope="module", name="service")
def fixture_service():
    """Fixture to create a CustomerAccountStatusService with a populated in-memory database."""
    db = SqliteDB(in_memory=True)
    create_and_populate_db(db)
    return CustomerAccountStatusService(db)


def test_find_by_id_existing_customer(service):
    """Test finding account status by existing customer ID."""
    result = service.find_by_id(1111)
    assert result == "Good-standing", "Expected 'Good-standing' for customer id = 1111"


def test_find_by_id_non_existing_customer(service):
    """Test finding account status by non-existing customer ID."""
    result = service.find_by_id(999)
    assert result is None, "Expected None for non-existing customer ID"


def test_find_by_name_existing_customer(service):
    """Test finding account status by existing customer name."""
    result = service.find_by_name("Hilda")
    assert result == "Delinquent", "Expected 'Delinquent' for customer name 'Hilda'"
    result = service.find_by_name("Loren")
    assert result == "Good-standing", "Expected 'Good-standing' for customer name 'Loren'"


def test_find_by_name_non_existing_customer(service):
    """Test finding account status by non-existing customer name."""
    result = service.find_by_name("albert")
    assert result is None, "Expected None for non-existing customer name"


def test_find_by_email_existing_customer(service):
    """Test finding account status by existing customer name."""
    result = service.find_by_email("halida@gmail.com")
    assert result == "Delinquent", "Expected 'Delinquent' for customer email 'halida@gmail.com'"
    result = service.find_by_email("loren@gmail.com")
    assert result == "Good-standing", "Expected 'Good-standing' for customer email 'loren@gmail.com'"


def test_find_by_email_non_existing_customer(service):
    """Test finding account status by non-existing customer name."""
    result = service.find_by_email("albert@test.com")
    assert result is None, "Expected None for non-existing customer name"
