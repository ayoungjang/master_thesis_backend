from datetime import datetime
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame
from src.common.consts import RESULT_PATH
router = APIRouter()

@router.get("/results/{type}/{timestamp}/{filename}")
async def get_result_file(type: str, timestamp:str,filename: str):
    file_path = os.path.join(RESULT_PATH, type,timestamp, filename)
    print(file_path)
    if not os.path.exists(file_path):
        print("error")
    return FileResponse(file_path)