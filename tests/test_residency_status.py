"""Unit tests for CustomerAccountStatusService."""
import pytest
from app.db.db import ResidencyStatus, SqliteDB, create_and_populate_db
from app.services.residency_status import ResidencyStatusService


@pytest.fixture(scope="module", name="service")
def fixture_service():
    """Fixture to create a CustomerCreditScoreService with a populated in-memory database."""
    db = SqliteDB(in_memory=True)
    create_and_populate_db(db)
    return ResidencyStatusService(db)


def test_find_by_id_existing_customer(service):
    """Test finding account status by existing customer ID."""
    result = service.find_by_id(1111)
    assert result == ResidencyStatus.CITIZEN, "Expected 'Citizen' for customer id = 1111"


def test_find_by_id_non_existing_customer(service):
    """Test finding account status by non-existing customer ID."""
    result = service.find_by_id(999)
    assert result is None, "Expected None for non-existing customer ID"


def test_find_by_name_existing_customer(service):
    """Test finding account status by existing customer name."""
    result = service.find_by_name("Matt")
    assert result ==  ResidencyStatus.PERMANENT_RESIDENT, "Expected 'PERMANENT_RESIDENT' for customer name 'Matt'"
    result = service.find_by_name("Andy")
    assert result ==  ResidencyStatus.NON_RESIDENT, "Expected 'NON_RESIDENT' for customer name 'Andy'"
    result = service.find_by_name("Loren")
    assert result ==  ResidencyStatus.CITIZEN, "Expected 'CITIZEN' for customer name 'Loren'"


def test_find_by_name_non_existing_customer(service):
    """Test finding account status by non-existing customer name."""
    result = service.find_by_name("albert")
    assert result is None, "Expected None for non-existing customer name"


def test_find_by_email_existing_customer(service):
    """Test finding account status by existing customer name."""
    result = service.find_by_email("halida@gmail.com")
    assert result == ResidencyStatus.CITIZEN, "Expected 'CITIZEN' for customer email 'halida@gmail.com'"
    result = service.find_by_email("loren@gmail.com")
    assert result == ResidencyStatus.CITIZEN, "Expected 'CITIZEN' for customer email 'loren@gmail.com'"


def test_find_by_email_non_existing_customer(service):
    """Test finding account status by non-existing customer name."""
    result = service.find_by_email("albert@test.com")
    assert result is None, "Expected None for non-existing customer name"
