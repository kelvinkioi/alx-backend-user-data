#!/usr/bin/env python3
"""
DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db",
                                     echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        create a user object and save it to the database
        Args:
            email - str
            hashed_password - str
        Return:
            a user object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        method takes in arbitrary keyword arguments and returns the first row
        found in the users table as filtered by the method’s input arguments
        Args:
            attributes (dict): a dictionary of attributes
        Return:
            matching user or raise error
        """
        all_users = self._session.query(User)
        for att, value in kwargs.items():
            if att not in User.__dict__:
                raise InvalidRequestError
            for usr in all_users:
                if getattr(usr, att) == value:
                    return usr
        raise NoResultFound

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        this method uses find_user_by to locate the user to
        update, then will update the user’s attributes as
        passed in the method’s arguments then commit changes
        to the database
        """
        try:
            usr = self.find_user_by(id=user_id)
        except NoResultFound:
            raise ValueError()
        for att, value in kwargs.items():
            if hasattr(usr, att):
                setattr(usr, att, value)
            else:
                raise ValueError
        self._session.commit()
