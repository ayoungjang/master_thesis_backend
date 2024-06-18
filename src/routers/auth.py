from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import bcrypt
import jwt
from datetime import datetime, timedelta
from src.common.consts import JWT_SECRET, JWT_ALGORITHM
from src.database.conn import db
from src.database.schemas import Users
from src.database.models import Token, UserRegister,UserLogin


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
    request: UserRegister,
    session: Session = Depends(db.session),
):
    try:
      id = request.id
      pw = request.pw
      name = request.name
      is_exist = await is_id_exist(id)
      if not id or not pw:
          return JSONResponse(
              status_code=400,
              content=dict(status=400, msg="ID and PW must be provided'"),
          )
      if is_exist:
          return JSONResponse(
              status_code=400, content=dict(status=400, msg="ID EXISTED")
          )
      hash_pw = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

      user = Users.create(
          session,
          auto_commit=True,
          pw=hash_pw,
          id=id,
          name=name
      )
      
      token_data = {
      "user_id": user.user_id.hex(),
      "id": user.id,
      }

      return JSONResponse(
      status_code=200,
      content=dict(
          status=200, access_token=f"{create_access_token(data=token_data)}"
      )
     )
    
    except Exception as e:
        return JSONResponse(
            status_code=500, content=dict(msg="Internal Server Error", detail=str(e))
        )




@auth.post(
    "/login", tags=["Authorization"], status_code=200, response_model=Token
)
async def login(request: UserLogin):
    id = request.id
    pw = request.pw
    
    is_exist = await is_id_exist(id)

    if not id or not pw:
        return JSONResponse(
            status_code=400, content=dict(msg="ID and PW must be provided")
        )
    
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

    user = Users.get(id=id)
    if not user:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

    is_verified = bcrypt.checkpw(pw.encode("utf-8"), user.pw)  # user.pw is already bytes
    

    if not is_verified:
        return JSONResponse(
            status_code=400, content=dict(status=400, msg="NO_MATCH_USER")
        )

    
    token_data = {
      "user_id": user.user_id.hex(),
      "id": user.id,
      }
    
    return JSONResponse(
    status_code=200,
    content=dict(
        status=200, access_token=f"{create_access_token(data=token_data)}"
    )
    )
    




def create_access_token(*, data: dict = None, expires_delta: int = 2):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    to_encode.setdefault("sub", data.get("sub"))
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt