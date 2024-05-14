from dataclasses import dataclass
import os
from os import path, environ
from dotenv import load_dotenv

load_dotenv()

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    기본 Configuration
    """

    BASE_DIR: str = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_URL: str = environ.get(
        "DB_URL",
        "mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_SCHEMA}?charset=utf8mb4",
    )


@dataclass
class LocalConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    DEBUG: bool = True


@dataclass
class ProdConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class TestConfig(Config):
    DB_URL: str = (
        "mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_SCHEMA}?charset=utf8mb4"
    )
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    api_env = os.getenv("API_ENV", "local")
    selected_config = config[api_env]()

    selected_config.DB_URL = selected_config.DB_URL.format(
        DB_USER=os.getenv("DB_USER"),
        DB_PASS=os.getenv("DB_PASS"),
        DB_HOST=os.getenv("DB_HOST"),
        DB_SCHEMA=os.getenv("DB_SCHEMA"),
    )

    return selected_config
