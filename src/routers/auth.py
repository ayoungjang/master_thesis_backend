from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import bcrypt
import jwt
from datetime import datetime, timedelta
from src.common.consts import JWT_SECRET, JWT_ALGORITHM
from src.database.conn import db
from src.database.schemas import Users
from src.database.models import Token



auth = APIRouter(prefix="/auth")


async def is_id_exist(id: str):
    get_id = Users.get(id=id)
    if get_id:
        return True
    return False


@auth.post(
    "/register",
    tags=["Authorization"],
    status_code=201,
    # response_model=Token,
)
async def register(
    id: str,
    pw: str,
    session: Session = Depends(db.session),
):
    try:
      is_exist = await is_id_exist(id)
      if not id or not pw:
          return JSONResponse(
              status_code=400,
              content=dict(status=400, msg="id and PW must be provided'"),
          )
      if is_exist:
          return JSONResponse(
              status_code=400, content=dict(status=400, msg="EMAIL_EXISTS")
          )
      hash_pw = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

      user = Users.create(
          session,
          auto_commit=True,
          pw=hash_pw,
          id=id
      )
      token_data = {
      "user_id": user.user_id.hex(),
      "id": user.id,
      };

      return JSONResponse(
      status_code=200,
      content=dict(
          status=200, Authorization=f"{create_access_token(data=token_data)}"
      )
     )
    
    except Exception as e:
        return JSONResponse(
            status_code=500, content=dict(msg="Internal Server Error", detail=str(e))
        )



@auth.post(
    "/login", tags=["Authorization"], status_code=200, response_model=Token
)
async def login(id: str, pw: str ):
  is_exist = await is_id_exist(id)
  if not id or not pw:
      return JSONResponse(
          status_code=400, content=dict(msg="id and PW must be provided")
      )
  if not is_exist:
      return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

  user = Users.get(id=id)
  is_verified = bcrypt.checkpw(pw.encode("utf-8"), user.pw.encode("utf-8"))
  if not is_verified:
      return JSONResponse(
          status_code=400, content=dict(status=400, msg="NO_MACTH_USER")
      )
  token_data = {
      "user_id": user.user_id.hex(),
  }

  token = dict(Authorization=f"Bearer {create_access_token(data=token_data)}")
  return token

  


@auth.post("/token", tags=["Authorization"])
async def token_login(
    token:str,
    session:Session = Depends(db.session)
):
    auth_headers = {
        "Authorization": f"Bearer {token}" ,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    
    is_exist = await is_id_exist(id)
    if is_exist:
        token = await login(id=id)
        return token

    else:
        
        user = Users.create(
            session,
            auto_commit=True,
            id=id,
        )

        token_data = {
        "id": user.id,
        "pw": user.pw,
        };

        return JSONResponse(
        status_code=200,
        content=dict(
            status=200, Authorization=f"{create_access_token(data=token_data)}"
        ))
        


def create_access_token(*, data: dict = None, expires_delta: int = 2):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    to_encode.setdefault("sub", data.get("sub"))
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
