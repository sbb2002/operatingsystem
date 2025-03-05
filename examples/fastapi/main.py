from fastapi import FastAPI, Request, File, UploadFile, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import whisper
import torch
import huggingface_hub
from transformers import pipeline

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
    
    ## Taking OGG files from the client
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())  # 🔹 await 사용해서 비동기 읽기
        
    ## STT process
    model_whisper = whisper.load_model('tiny')
    stt_result = model_whisper.transcribe(file_location)['text']
    # print(stt_result['text'])
    
    ## LLM Process
    torch.cuda.empty_cache()
    model_llm = "meta-llama/Llama-3.2-1B-Instruct"
    pipe_llm = pipeline(
        'text-generation',
        model=model_llm,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    messages = [
        {"role": "system", "content": "You are a special agent for helping me. You should answer shortly."},
        {"role": "user", "content": stt_result},
    ]
    llm_result = pipe_llm(
        messages,
        max_new_tokens=256,
    )[0]["generated_text"][-1]['content']
    
    print("Q)\n", stt_result, "\n\nA)\n", llm_result)
    
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
    
