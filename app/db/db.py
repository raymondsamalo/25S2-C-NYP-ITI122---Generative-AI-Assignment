from abc import ABC, abstractmethod
import pathlib
from enum import StrEnum
from sqlalchemy import Engine
from sqlalchemy.dialects import postgresql  # Works for SQLite too
from sqlmodel import Column, Field, Session, SQLModel, create_engine, Enum


class AccountStatus(StrEnum):
    """
    Enumeration representing different account statuses.
    """
    GOOD_STANDING = "Good-standing"
    CLOSED = "Closed"
    DELIQUENT = "Delinquent"


class ResidencyStatus(StrEnum):
    """
    Enumeration representing different residency statuses.
    """
    PERMANENT_RESIDENT = "permanent-resident"
    CITIZEN = "citizen"
    NON_RESIDENT = "non-resident"


class Customer(SQLModel, table=True):
    """
    Represents a customer in the database.  
    Attributes:
        ID (int | None): The unique identifier for the customer. This is the primary key.
        name (str): The name of the customer.
        email (str): The email address of the customer.
    """
    ID: int | None = Field(default=None, primary_key=True)
    name: str
    email: str


class CustomerCreditScore(SQLModel, table=True):
    """
    Represents the credit score of a customer in the database.

    Attributes:
        ID (int | None): The unique identifier for the customer. This serves as a 
            foreign key referencing the 'customer.ID' field in the database.
        credit_score (int | None): The credit score of the customer. Defaults to None.
    """
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    credit_score: int | None = None


class CustomerAccountStatus(SQLModel, table=True):
    """
    CustomerAccountStatus

    This class represents the status of a customer account in the database. 
    It is a SQLModel table that maps to the database schema.

    Attributes:
        ID (int | None): The primary key of the table, 
        which is also a foreign key referencing the `ID` field in the `customer` table.
        account_status (AccountStatus): The status of the customer account, 
        represented as an enumeration of type `AccountStatus`.
    """
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    account_status:  AccountStatus = Field(
        default=None, sa_column=Column(Enum(AccountStatus)))


class CustomerPRStatus(SQLModel, table=True):
    """
    CustomerPRStatus is a database model representing the PR (Permanent Residency) 
    status of a customer.

    Attributes:
        ID (int | None): The primary key of the table, 
        which is also a foreign key referencing the `ID` field in the `customer` table.
        pr_status (bool): A boolean field indicating the PR status of the customer.
    """
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    pr_status: bool


class DB(ABC):
    """ Abstract database interface """
    def __init__(self) -> None:
        self._engine = None

    @property
    def engine(self):
        """ create database engine and ensure only 1 engine per object instance """
        if self._engine is None:
            self._engine = self.create_engine()
        return self._engine

    @abstractmethod
    def create_engine(self) -> Engine:
        """ actual engine creation, override this to customise """

    def session(self) -> Session:
        """ return database session """
        return Session(self.engine)

    @abstractmethod
    def add_if_not_exist(self, session, record):
        """ insert into database but ignore on conflict"""


class SqliteDB(DB):
    """
    Database wrapper
    """

    def __init__(self, in_memory:bool=False) -> None:
        super().__init__()
        if in_memory: # use in-memory database for testing
            self.path = "sqlite:///:memory:"
            return
        script_directory = pathlib.Path(__file__).parent
        data_path = script_directory.parent.parent / 'data' / 'database.sqlite'
        self.path = "sqlite:///"+data_path.resolve().as_posix()

    def create_engine(self):
        return create_engine(self.path)

    def session(self):
        """
            return database session
        """
        return Session(self.engine)

    def add_if_not_exist(self, session, record):
        """
        insert into database but ignore on conflict 
        """
        statement = (
            postgresql.insert(record.__class__)
            .values(**record.model_dump(exclude_unset=True))
            .on_conflict_do_nothing()
        )
        session.exec(statement)

def create_schema_if_not_exists(db:DB):
    """
    Creates the database schema if it does not already exist.

    This function initializes the database schema using SQLModel metadata. 
    It ensures that all tables defined in the SQLModel models are created 
    in the database associated with the provided database object.

    Args:
        db: A database object that provides access to the database engine.
    """
    SQLModel.metadata.create_all(db.engine)

def create_and_populate_db(db):
    """
    Creates and populates the database with initial data.

    This function initializes the database schema using SQLModel metadata and 
    populates it with predefined records for customers, their account statuses, 
    credit scores, and PR statuses. It ensures that duplicate records are not 
    added by using the `db.add_if_not_exist` method.

    Args:
        db: A database object that provides access to the database engine 
            and session management.

    Raises:
        Any exceptions raised during database operations, such as connection 
        issues or integrity errors, will propagate to the caller.
    """
    SQLModel.metadata.create_all(db.engine)
    records = [
        Customer(ID=1111, name="Loren", email="loren@gmail.com"),
        Customer(ID=2222, name="Matt", email="matt@yahoo.com"),
        Customer(ID=3333, name="Hilda", email="halida@gmail.com"),
        Customer(ID=4444, name="Andy", email="andy@gmail.com"),
        Customer(ID=5555, name="Kit", email="kit@yahho.com"),
        CustomerAccountStatus(
            ID=1111, account_status=AccountStatus.GOOD_STANDING),
        CustomerAccountStatus(
            ID=2222, account_status=AccountStatus.CLOSED),
        CustomerAccountStatus(
            ID=3333, account_status=AccountStatus.DELIQUENT),
        CustomerAccountStatus(
            ID=4444, account_status=AccountStatus.GOOD_STANDING),
        CustomerAccountStatus(
            ID=5555, account_status=AccountStatus.DELIQUENT),
        CustomerCreditScore(ID=1111, credit_score=455),
        CustomerCreditScore(ID=2222, credit_score=685),
        CustomerCreditScore(ID=3333, credit_score=825),
        CustomerCreditScore(ID=4444, credit_score=840),
        CustomerCreditScore(ID=5555, credit_score=350),
        CustomerPRStatus(ID=2222, pr_status=True),
        CustomerPRStatus(ID=4444, pr_status=False),
    ]
    with db.session() as session:
        for record in records:
            db.add_if_not_exist(session, record)
        session.commit()

