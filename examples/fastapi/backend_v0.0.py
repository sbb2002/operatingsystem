from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import shutil
import datetime

app = FastAPI()

# HTML 페이지 제공
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <body>
            <h2>Audio Recorder</h2>
            <button onclick="startRecording()">REC</button>
            <script>
                async function startRecording() {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const mediaRecorder = new MediaRecorder(stream);
                    const chunks = [];

                    mediaRecorder.ondataavailable = event => chunks.push(event.data);
                    mediaRecorder.onstop = async () => {
                        const blob = new Blob(chunks, { type: 'audio/wav' });
                        const formData = new FormData();
                        formData.append('file', blob, 'recording.wav');
                        await fetch('/upload/', {
                            method: 'POST',
                            body: formData
                        });
                        alert('Audio uploaded!');
                    };

                    mediaRecorder.start();
                    setTimeout(() => mediaRecorder.stop(), 5000); // 5초간 녹음
                }
            </script>
        </body>
    </html>
    """

# 오디오 파일 업로드 처리
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{current_time}.wav"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Audio uploaded successfully", "filename": filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
