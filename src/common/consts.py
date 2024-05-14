import os

JWT_SECRET = "SDIFJEI<OU!"
JWT_ALGORITHM = "HS256"
EXCEPT_PATH_LIST = ["/", "/openapi.json"]
EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"
SERVER = "http://localhost:8080"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

