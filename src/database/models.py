from fastapi import Query
from .session import Base
from enum import Enum
from pydantic.main import BaseModel
from pydantic import BaseModel, Field

class UserLogin(BaseModel):
    id: str = None
    pw: str = None


class UserRegister(BaseModel):
    id:str=None
    pw: str = None
    name: str = None


class Token(BaseModel):
    Authorization: str = None


class UserToken(BaseModel):
    user_id: str = None

    @classmethod
    def from_attribute(cls, attribute):
        return cls(**attribute)

