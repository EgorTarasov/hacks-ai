from aiogram.types import User

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from db import models
from logging import Logger
from . import Base

from utils.logging import get_logger
from utils.settings import settings


class SQLManager:
    instance = None

    def __init__(self, log: Logger = get_logger("__sql_manager__")):
        self.log = log
        self._connect()
        self._update_db()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls.instance is None:
            cls.instance = super(SQLManager, cls).__new__(cls)
        return cls.instance

    def __del__(self):
        """Close the database connection when the object is destroyed"""
        self._close()

    def _connect(self) -> None:
        """Connect to the postgresql database"""
        self.engine = create_engine(f"sqlite:///{settings.sqlite_filepath}")
        Base.metadata.bind = self.engine
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def _close(self) -> None:
        """Closes the database connection"""
        self.session.close_all()

    def _update_db(self) -> None:
        """Create the database structure if it doesn't exist (update)"""
        # Create the tables if they don't exist
        Base.metadata.create_all(self.engine)

    def does_user_exist(self, user_id: int) -> bool:
        """Check if a user exists in the database"""
        return self.session.query(models.User).filter(models.User.id == user_id).first() is not None

    def save_user(self, user: User) -> None:
        if self.get_user(user.id):
            db_state = self.get_users_state(user.id)
            db_state.state = "train"
            db_state.train = None
            db_state.text = None
            db_state.voice_file = None
            self.session.commit()
            return None
        db_user = models.User(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            is_premium=user.is_premium
        )
        db_state = models.UserState(
            user_id=user.id,
            state="train"
        )
        self.session.add_all([db_user,db_state])
        self.session.commit()

    def get_user(self, user_id: int) -> User | None:
        db_user = self.session.query(models.User).filter(models.User.id == user_id).one_or_none()
        if db_user:
            user = User(
                id=db_user.id,
                is_bot=db_user.is_bot,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                username=db_user.username,
                language_code=db_user.language_code,
                is_premium=db_user.is_premium
            )
            return user

    def get_users_state(self, user_id: int) -> models.UserState:
        db_state = self.session.query(models.UserState).filter(models.UserState.user_id == user_id).one_or_none()
        if not db_state:
            raise KeyError
        return db_state

    def update_users_state(self, state: models.UserState):
        self.session.commit()








