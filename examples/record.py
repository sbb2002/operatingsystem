import pyaudio
import numpy as np
# import wave
from scipy.io import wavfile

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 22050

p = pyaudio.PyAudio()
for index in range(p.get_device_count()):
    desc = p.get_device_info_by_index(index)
    print("DEVICE: {device}, INDEX: {index}, RATE: {rate} ".format(
        device=desc["name"], index=index, rate=int(desc["defaultSampleRate"])))
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print('Start recording.')

def check_silent(data_array, threshold):
    # Average decibel of a frame
    avg_decibel = np.abs(data_array).mean()
    return avg_decibel < threshold

def decide_threshold(frames, threshold=0):
    avg_decibel_on_frames = np.abs(np.hstack(frames)).mean()
    if avg_decibel_on_frames > threshold:
        return avg_decibel_on_frames / 2
    else:
        return threshold

frames = []
on_air = int(RATE / CHUNK * 1)
recording_limit = on_air * 10
threshold = 0
# for i in range(0,int(RATE / CHUNK * seconds)):
while on_air > 0:
    # Record each frame
    data = stream.read(CHUNK)
    data_array = np.frombuffer(data, dtype=np.int16)
    frames.append(data_array)
    
    # If silent or reach the recording limit, on_air -= 1
    threshold = decide_threshold(frames, threshold)
    is_silent = check_silent(data_array, threshold)
    if is_silent or len(frames) >= recording_limit:
        on_air -= 1
    else:
        on_air = int(RATE / CHUNK * 1)
    
frames = np.hstack(frames)
print(frames.shape)

wavfile.write('test.wav', rate=22050, data=frames)

print('Record stopped')

stream.stop_stream()
stream.close()
p.terminate()

# wf = wave.open("output.wav",'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(b''.join(frames))
# wf.close()


## TODO
'''
녹음 기능은 구현했다.
폰에서 녹음하는 기능을 넣어야하는데,
fastapi로 webUI로 접근하도록 하자.
'''