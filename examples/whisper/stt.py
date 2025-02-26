import whisper
import time

# soundfile_path = r'D:\PythonWorkspace\operator_kayoko\examples\fastapi\web-dictaphone\uploads\rec_20250227015139.ogg'
soundfile_path = r'D:\PythonWorkspace\operator_kayoko\examples\fastapi\web-dictaphone\uploads\rec_20250227024158.ogg'
model_name = 'tiny'

model = whisper.load_model(model_name)

t_start = time.time()
result = model.transcribe(soundfile_path)
t_end = time.time()

print(result["text"])
print(f"Elapsed {t_end - t_start:.1f}s - {model_name}")