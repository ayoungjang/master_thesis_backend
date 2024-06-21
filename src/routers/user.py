from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Optional
from src.database.conn import db

from sqlalchemy.dialects.mysql import BINARY
from src.database.schemas import Users
from src.common.lib import uuid_to_bytes

user = APIRouter(prefix="/user")


@user.get("", tags=["User"], status_code=200)
async def get_user(
    session: Session = Depends(db.session),
):
    try:
        users_obj = Users.filter(session)
        users = users_obj.all()

        return [
            {
                "user_id": user.user_id.hex(),
                "name": user.name,
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@user.get("/token", tags=["User"], status_code=200)
async def token_login(
    request: Request,
    session: Session = Depends(db.session),
):
    try:
        
        user_id = bytes.fromhex(request.state.user.user_id)

        user = Users.get(session, user_id=user_id)
        if user:
            headers = request.headers
            return JSONResponse(
                status_code=200,
                content=dict(status=200, data=headers.get("Authorization")),
            )
        else:
            raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@user.get("/me", tags=["User"], status_code=200)
async def get_user_me(
    request: Request,
    session: Session = Depends(db.session),
):
    try:
        user_id = bytes.fromhex(request.state.user.user_id)

        user = Users.get(session, user_id=user_id)

        return JSONResponse(
            status_code=200,
            content=dict(
                {
                    "user_id": user.user_id.hex(),
                    "name": user.name,
                }
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@user.delete("/{user_id}", tags=["User"], status_code=200)
async def delete_user(
    user_id: str,
    session: Session = Depends(db.session),
):
    try:
        user_id = bytes.fromhex(user_id)
        users_obj = Users.get(session, user_id=user_id)

        if not users_obj:
            return JSONResponse(
                status_code=400, content=dict(msg="this user does not existed")
            )

        session.delete(users_obj)
        session.commit()

        return JSONResponse(
            status_code=200, content=dict(status=200, msg="user deleted successfully")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@user.patch(
    "/{user_id}",
    tags=["User"],
    status_code=200,
    response_model=dict,
    description="edit user information",
)
def patch_user(
    request: Request,
    user_id: str,
    name: Optional[str] = None,
    pw: Optional[str] = None,
    session: Session = Depends(db.session),
):
    try:
        user_id = bytes.fromhex(user_id)
        get_user_record = Users.get(session, user_id=user_id)
        get_user_record.filter(session)

        if not get_user_record:
            return JSONResponse(
                status_code=400, contnet=dict(status=400, msg="this user not exsited")
            )

        get_user_record._session = session
        get_user_record._q = session.query(Users).filter_by(user_id=user_id)
        get_user_record.served = False
        get_user_record.update(auto_commit=True, name=name)

        updated_user = Users.get(session, user_id=user_id)
        updated_user.filter(session)

        request.state.user = updated_user

        return JSONResponse(
            status_code=200, content=dict(status=200, msg="user updated successfully")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
