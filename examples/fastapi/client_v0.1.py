# FastAPI를 사용해 클라이언트 측 HTML 제공
# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# HTML 및 JavaScript 코드
html_content = """
<!DOCTYPE html>
<html>
<head>
  <title>Audio Recorder</title>
</head>
<body>
  <h2>Audio Recorder</h2>
  <button id="recordBtn">Start Recording</button>
  <button id="stopBtn" disabled>Stop Recording</button>
  <audio id="audioPlayback" controls></audio>
  <script>
    let mediaRecorder;
    let audioChunks = [];

    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const audioPlayback = document.getElementById('audioPlayback');

    recordBtn.addEventListener('click', async () => {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioPlayback.src = URL.createObjectURL(audioBlob);
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');
        const response = await fetch('/upload/', { method: 'POST', body: formData });
        const result = await response.json();
        alert(`Server Response: ${result.message}`);
      };
      audioChunks = [];
      mediaRecorder.start();
      recordBtn.disabled = true;
      stopBtn.disabled = false;
    });
    stopBtn.addEventListener('click', () => {
      mediaRecorder.stop();
      recordBtn.disabled = false;
      stopBtn.disabled = true;
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_html():
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
