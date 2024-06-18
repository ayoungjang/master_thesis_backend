from datetime import datetime
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame
from src.common.consts import RESULT_PATH
router = APIRouter()


@router.get("/")
async def index():
    """
    ELB 상태 체크용 API
    :return:
    """
    current_time = datetime.utcnow()
    return Response(
        f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크용 API
    :return:
    """
    print("state.user", request.state.user)
    try:
        a = 1 / 0
    except Exception as e:
        request.state.inspect = frame()
        raise e
    current_time = datetime.utcnow()
    return Response(
        f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )


@router.get("/results/{type}/{timestamp}/{filename}")
async def get_result_file(type: str, timestamp:str,filename: str):
    file_path = os.path.join(RESULT_PATH, type,timestamp, filename)
    print(file_path)
    if not os.path.exists(file_path):
        print("error")
    return FileResponse(file_path)