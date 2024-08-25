import datetime
from fastapi import APIRouter, File, Form,UploadFile,Query
import shutil
import os
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from src.database.schemas import Users
from src.database.models import Token
import subprocess 
from src.common.consts import EXCEL_PATH, RESULT_PATH
import json
import pandas as pd
import matplotlib.pyplot as plt

if not os.path.exists(EXCEL_PATH):
    os.makedirs(EXCEL_PATH)
if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)



excel = APIRouter(prefix="/excel")

@excel.post("/upload", tags=["Excel"], status_code=201)
async def upload_file(  type: str = Form(...), data: UploadFile = File(...), refer: UploadFile = File(...)):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if not os.path.exists(os.path.join(EXCEL_PATH,timestamp)):
            os.mkdir(os.path.join(EXCEL_PATH,timestamp))
    
        data_file_path = os.path.join(EXCEL_PATH,timestamp, data.filename)
        with open(data_file_path, "wb") as buffer:
            shutil.copyfileobj(data.file, buffer)

        ref_file_path = os.path.join(EXCEL_PATH,timestamp, refer.filename)
        with open(ref_file_path, "wb") as buffer:
            shutil.copyfileobj(refer.file, buffer)

        # Create a unique output directory based on the current timestamp
        result_dir = os.path.join(RESULT_PATH, type.lower(),timestamp)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        
        
        script_path = os.path.abspath(f"src/Rscript/{type.lower()}/index.R")
        
        # Find Rscript path
        rscript_path = subprocess.check_output(["which", "Rscript"]).strip().decode('utf-8')
        
        subprocess.call([rscript_path, "--vanilla", script_path, data_file_path, ref_file_path, result_dir])

        # Get the list of generated plot files
        plot_files = [os.path.join(result_dir, f) for f in os.listdir(result_dir) if f.endswith(".json")]

        
        plot_files_with_names = [{"path": os.path.join(f),"dir":f.split('/')[2], "name": f.split('/')[3].split('.')[0]} for f in plot_files]

        print(plot_files_with_names)
        if not plot_files:
            print("plot not found")
            # raise DataProcessingError(msg="Result plot not found", detail="The R script did not generate the expected result plot.")
        # return JSONResponse(content={"msg": "file upload success", "files": "test"})
        return JSONResponse(content={"msg": "file upload success", "data": plot_files_with_names})
        #return JSONResponse(content={"msg": "file upload success", "dir": result_dir,"files":plot_files_with_names})
    except subprocess.CalledProcessError as e:
        print("data processing err")
        # raise DataProcessingError(ex=e)
    except Exception as e:
        print("file upload err",e)
        # raise FileUploadError(ex=e)
        # raise HTTPException(status_code=StatusCode.HTTP_404, detail="File not found")
@excel.get("/plots/{type}/{timestamp}/{name}", tags=["Excel"], status_code=201)
def getTypeData(type: str, timestamp: str, name: str):
    json_file_path = os.path.join(RESULT_PATH, type.lower(), timestamp, f"{name}.json")
   
    if not os.path.exists(json_file_path):
        return JSONResponse(status_code=404, content={"message": "File not found"})
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    return JSONResponse(content=data)