import uvicorn
from dataclasses import asdict
from fastapi import FastAPI, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from src.database.conn import db
from src.common.config import conf

from src.middlewares.token_validator import access_control
from src.middlewares.trusted_hosts import TrustedHostMiddleware
from src.routers.user import user
from src.routers.auth import auth
from src.routers.excel import excel
from src.routers.index import router

import dotenv
import os

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

API_KEY_HEADER = HTTPBearer()



def create_app():
    """
    :return:
    """
    c = conf()
    app = FastAPI(docs_url="/docs/api", redoc_url="/redoc/api")
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)  # database initialization

    # middleware
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=conf().TRUSTED_HOSTS,
        except_path=["/health"],
    )
    app.include_router(router)
    app.include_router(auth)
    app.include_router(user,prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(excel,prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    return app
    

app = create_app()


if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("main:app", port=8000, reload=True)
