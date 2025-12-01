"""
Unit tests for the database module."""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlmodel import SQLModel

from app.db import Customer, SqliteDB
from app.db.db import create_and_populate_db


def test_sqlite_db_initialization():
    """
    Test the initialization of the SqliteDB class.
    Ensures that the database path is set correctly.
    """
    # Arrange & Act
    db = SqliteDB()

    # Assert
    expected_path_suffix = "data/database.sqlite"
    assert db.path.endswith(
        expected_path_suffix), f"Database path should end with {expected_path_suffix}"

    db_in_memory = SqliteDB(in_memory=True)
    assert db_in_memory.path == "sqlite:///:memory:", "In-memory path != 'sqlite:///:memory:'"


def test_create_engine():
    """
    Test the create_engine method of the SqliteDB class.
    Ensures that the method returns a valid SQLAlchemy Engine instance.
    """
    # Arrange
    db = SqliteDB()

    # Act
    engine = db.create_engine()

    # Assert
    assert isinstance(
        engine, Engine), "create_engine should return an instance of sqlalchemy.Engine"
    assert engine.url.database.endswith(
        "database.sqlite"), "Engine should point to the correct SQLite database file"


def test_session():
    """
    Test the session method of the SqliteDB class.
    Ensures that the method returns a valid SQLAlchemy Session instance.
    """
    # Arrange
    db = SqliteDB(in_memory=True)

    # Act
    session = db.session()

    # Assert
    assert isinstance(
        session, SQLAlchemySession), "session should return an instance of sqlalchemy.orm.Session"


def test_add_if_not_exist():
    """
    Test the add_if_not_exist method of the SqliteDB class.
    Ensures that a record can be added without raising exceptions.
    """
    # Arrange
    db = SqliteDB(in_memory=True)
    SQLModel.metadata.create_all(db.engine)
    # Create a mock record (assuming Customer is a valid model)
    mock_record = Customer(
        ID=9999,  # Use a unique ID to avoid conflicts
        name="Test User",
        email="test@test.com"
    )

    # Act & Assert
    try:
        with db.session() as session:
            db.add_if_not_exist(session, mock_record)
            # Try adding the same record again
            db.add_if_not_exist(session, mock_record)
            session.commit()
            selected = session.get(Customer, mock_record.ID)
            assert selected is not None, "Record should be added to the database"
            assert selected.name == "Test User", "Record name should match the inserted value"
            assert selected.email == "test@test.com", "Record email should match the inserted value"
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"add_if_not_exist raised an exception: {e}"


def test_create_and_populate_db():
    """
    Test the create_and_populate_db function.
    Ensures that the database is created and populated without raising exceptions.
    """
    # Arrange
    db = SqliteDB()

    # Act & Assert
    try:
        create_and_populate_db(db)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"create_and_populate_db raised an exception: {e}"
