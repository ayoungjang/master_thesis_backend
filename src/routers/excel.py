import datetime
from fastapi import APIRouter, File,UploadFile,Query
import shutil
import os
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from src.database.schemas import Users
from src.database.models import Token
import subprocess 
from src.common.consts import EXCEL_PATH, RESULT_PATH



if not os.path.exists(EXCEL_PATH):
    os.makedirs(EXCEL_PATH)
if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)



excel = APIRouter(prefix="/excel")

@excel.post("/upload", tags=["Excel"], status_code=201)
async def upload_file(type: str = Query("Strip", enum=["Disk", "Strip"]), data: UploadFile = File(...), refer: UploadFile = File(...)):
    try:
        if not os.path.exists(EXCEL_PATH):
            os.mkdir(EXCEL_PATH)
    
        data_file_path = os.path.join(EXCEL_PATH, data.filename)
        with open(data_file_path, "wb") as buffer:
            shutil.copyfileobj(data.file, buffer)

        ref_file_path = os.path.join(EXCEL_PATH, refer.filename)
        with open(ref_file_path, "wb") as buffer:
            shutil.copyfileobj(refer.file, buffer)

        # Create a unique output directory based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        result_dir = os.path.join(RESULT_PATH, type.lower(),timestamp)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        
        
        script_path = os.path.abspath(f"src/Rscript/{type}/index.R")
        
        # Find Rscript path
        rscript_path = subprocess.check_output(["which", "Rscript"]).strip().decode('utf-8')
        
        subprocess.call([rscript_path, "--vanilla", script_path, data_file_path, ref_file_path, result_dir])

        # Get the list of generated plot files
        plot_files = [os.path.join(result_dir, f) for f in os.listdir(result_dir) if f.endswith(".png")]
        print()
        plot_files_with_names = [{"path": os.path.join(f), "name": f.split('_')[1].split('.')[0]} for f in plot_files]

        
        if not plot_files:
            print("plot not found")
            # raise DataProcessingError(msg="Result plot not found", detail="The R script did not generate the expected result plot.")

        return JSONResponse(content={"msg": "file upload success", "files": plot_files_with_names})
    except subprocess.CalledProcessError as e:
        print("data processing err")
        # raise DataProcessingError(ex=e)
    except Exception as e:
        print("file upload err")
        # raise FileUploadError(ex=e)
    

        # raise HTTPException(status_code=StatusCode.HTTP_404, detail="File not found")
    
