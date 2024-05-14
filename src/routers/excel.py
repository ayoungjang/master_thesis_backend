from fastapi import APIRouter, File,UploadFile,Query
import shutil
import os
from starlette.responses import JSONResponse
from src.database.schemas import Users
from src.database.models import Token
import subprocess 

FILE_PATH = "./Rscript/disk/index.R"
EXCEL_PATH="excels"

excel = APIRouter(prefix="/excel")

@excel.post("/upload",
           tags=["Excel"],
           status_code=201,
           )

async def upload_file(
    type=Query("Disk",enum=["Disk","Strip"])
    ,data:UploadFile=File(...),refer:UploadFile=File(...)):
      try:
          
          if type is "Strip":
            if not os.path.exists(EXCEL_PATH):
                os.mkdir(EXCEL_PATH)

            file_path = os.path.join(EXCEL_PATH,data.filename)
            with open(file_path,"wb") as buffer:
                shutil.copyfileobj(data.file,buffer)

            file_path = os.path.join(EXCEL_PATH,refer.filename)
            with open(file_path,"wb") as buffer:
                shutil.copyfileobj(refer.file,buffer)

            subprocess.call(["/usr/bin/Rscript", "--vanilla",FILE_PATH])
            
            return JSONResponse(content={"msg":"file upload success"})
          else:
            if not os.path.exists(EXCEL_PATH):
                os.mkdir(EXCEL_PATH)

            file_path = os.path.join(EXCEL_PATH,data.filename)
            with open(file_path,"wb") as buffer:
                shutil.copyfileobj(data.file,buffer)

            file_path = os.path.join(EXCEL_PATH,refer.filename)
            with open(file_path,"wb") as buffer:
                shutil.copyfileobj(refer.file,buffer)

            subprocess.call(["/usr/bin/Rscript", "--vanilla",FILE_PATH])
            
            return JSONResponse(content={"msg":"file upload success"})
              
      except Exception as e:
          return JSONResponse(content={"msg" : "err occured{strf(e)}"}, status_code=500)

