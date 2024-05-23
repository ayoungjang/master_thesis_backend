from fastapi import FastAPI
from sqlalchemy import Table, Column, String, BINARY, MetaData, create_engine, inspect,DateTime,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.common.lib import generate_random_uuid
import datetime

class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        self._metadata = MetaData()
        self._base = declarative_base()  # Add this line
        if app is not None:
            self.init_app(app=app, **kwargs)
    def init_app(self, app: FastAPI, **kwargs):
        """
        DB 초기화 함수
        :param app: FastAPI 인스턴스
        :param kwargs:
        :return:
        """
        database_url = kwargs.get("DB_URL")
        self._engine = create_engine(
            database_url,
          connect_args={"check_same_thread": False}
        )

        self._session = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        self.create_table()  # Ensure tables are created when the app initializes


    def get_db(self):
        """
        요청마다 DB 세션 유지 함수
        :return:
        """
        if self._session is None:
            raise Exception("must be called 'init_app'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()
    
    def create_table(self):
        inspector = inspect(self._engine)
        if not inspector.has_table('user'):
            user = Table('user', self._metadata,
                        Column('id', String(length=60), nullable=True),
                        Column('pw', String(length=60), nullable=True),
                        Column('name', String(length=255), nullable=True),
                        Column('created_at', DateTime, default=func.now()),
                        Column('updated_at', DateTime, default=func.now(), onupdate=func.now()),
                        Column('user_id', BINARY, primary_key=True, default=generate_random_uuid, unique=True, nullable=False))
            self._metadata.create_all(self._engine)


    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()
Base = declarative_base()

