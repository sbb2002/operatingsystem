from fastapi import FastAPI
import uvicorn
import pyaudio
import numpy as np
from scipy.io import wavfile
import datetime

app = FastAPI()

@app.get("/record/")
def record_audio():
    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print('Start recording.')

    frames = []
    on_air = int(RATE / CHUNK * 1)
    recording_limit = on_air * 10
    threshold = 0

    def check_silent(data_array, threshold):
        return np.abs(data_array).mean() < threshold

    def decide_threshold(frames, threshold=0):
        avg = np.abs(np.hstack(frames)).mean()
        return avg / 2 if avg > threshold else threshold

    while on_air > 0:
        data = stream.read(CHUNK)
        data_array = np.frombuffer(data, dtype=np.int16)
        frames.append(data_array)
        threshold = decide_threshold(frames, threshold)
        if check_silent(data_array, threshold) or len(frames) >= recording_limit:
            on_air -= 1
        else:
            on_air = int(RATE / CHUNK * 1)

    frames = np.hstack(frames).astype(np.int16)
    filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    wavfile.write(filename, rate=RATE, data=frames)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    return {"message": "Recording complete", "filename": filename}

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="210.123.207.213", port=8000)
    
