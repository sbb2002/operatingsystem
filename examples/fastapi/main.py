from fastapi import FastAPI, Request, File, UploadFile, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

TEMPLATES_PATH = r'D:\PythonWorkspace\operator_kayoko\examples\fastapi\web-dictaphone'
UPLOAD_FOLDER = os.path.join(TEMPLATES_PATH, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요에 따라 특정 도메인으로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 제공
app.mount("/scripts", StaticFiles(directory=f"{TEMPLATES_PATH}/scripts"), name="scripts")
app.mount("/styles", StaticFiles(directory=f"{TEMPLATES_PATH}/styles"), name="styles")
app.mount("/app-icons", StaticFiles(directory=f"{TEMPLATES_PATH}/app-icons"), name="app-icons")

templates = Jinja2Templates(directory=TEMPLATES_PATH)

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):  # 🔹 multipart/form-data 형식 받도록 설정
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())  # 🔹 await 사용해서 비동기 읽기
    
    return {"message": "File uploaded successfully", "filename": file.filename}


if __name__ == "__main__":
    import uvicorn
    import socket
    import os
    
    ipaddr = socket.gethostbyname(socket.gethostname())
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    print("IP: ", ipaddr)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))    
    SSL_KEYFILE_PATH = os.path.join(BASE_DIR, 'key.pem')
    SSL_CERTFILE_PATH = os.path.join(BASE_DIR, 'cert.pem')
    
    uvicorn.run(app, host=ipaddr, port=8000, ssl_keyfile=SSL_KEYFILE_PATH, ssl_certfile=SSL_CERTFILE_PATH)
    
