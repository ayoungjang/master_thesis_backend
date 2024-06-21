import os

JWT_SECRET = os.getenv("SCRET_KEY")
JWT_ALGORITHM = "HS256"
EXCEPT_PATH_LIST = ["/", "/openapi.json"]
EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"
SERVER = "http://localhost:8000"
EXCEL_PATH=os.getenv("EXCEL_PATH")
RESULT_PATH=os.getenv("RESULT_PATH")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

