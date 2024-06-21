from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    BINARY,
)
import sqlalchemy
from sqlalchemy.orm import Session
from src.database.conn import Base, db
from src.common.lib import generate_random_uuid

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    def __init__(self):
        super().__init__()
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [
            c
            for c in self.__table__.columns
            if c.primary_key is False and c.name != "created_at"
        ]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        :param session:
        :param auto_commit
        :param kwargs
        :return:
        """
        obj = cls()
        try:
            for col in obj.all_columns():
                col_name = col.name
                if col_name in kwargs:
                    setattr(obj, col_name, kwargs.get(col_name))

            session.add(obj)
            session.flush()
            if auto_commit:
                session.commit()
            return obj
        except Exception as e:
            session.rollback()

            raise e

    @classmethod
    def get(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """

        sess = next(db.session()) if not session else session
        query = sess.query(cls)

        for key, val in kwargs.items():
            col = getattr(cls, key)
            if isinstance(col.property, sqlalchemy.orm.properties.ColumnProperty):
                query = query.filter(col == val)

        if query.count() > 1:
            raise Exception(
                "Only one row is supposed to be returned, but got more than one."
            )
        result = query.first()
        sess.close()
        return result

    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        cond = []

        for key, val in kwargs.items():
            key = key.split("__")

            if len(key) > 2:
                raise Exception("No 2 more dunders")

            col = getattr(cls, key[0])

            if len(key) == 1:
                cond.append((col == val))
            elif len(key) == 2 and key[1] == "gt":
                cond.append((col > val))
            elif len(key) == 2 and key[1] == "gte":
                cond.append((col >= val))
            elif len(key) == 2 and key[1] == "lt":
                cond.append((col < val))
            elif len(key) == 2 and key[1] == "lte":
                cond.append((col <= val))
            elif len(key) == 2 and key[1] == "in":
                cond.append((col.in_(val)))

        obj = cls()

        if session:
            obj._session = session
            obj.served = True
        else:
            obj._session = next(db.session())
            obj.served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)

        obj._q = query
        return obj

    @classmethod
    def cls_attr(cls, col_name=None):
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    def order_by(self, *args: str):
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = (
                self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
            )
        return self

    def update(self, auto_commit: bool = False, **kwargs):
        obj = self._q.one()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self._session.flush()

        if auto_commit:
            self._session.commit()

        return obj

    def first(self):
        result = self._q.first()
        self.close()
        return result

    def delete(self, auto_commit: bool = False):
        self._q.delete()
        if auto_commit:
            self._session.commit()

    def all(self):
        result = self._q.all()
        self.close()
        return result

    def count(self):
        result = self._q.count()
        self.close()
        return result

    def close(self):
        if not self.served:
            self._session.close()
        else:
            self._session.flush()


class Users(Base, BaseMixin):
    __tablename__ = "user"
    id = Column(String(length=60), nullable=True)
    pw = Column(String(length=60), nullable=True)
    name = Column(String(length=255), nullable=True)
    user_id = Column(
        BINARY,
        primary_key=True,
        default=generate_random_uuid,
        unique=True,
        nullable=False,
    )
