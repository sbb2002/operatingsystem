from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

TEMPLATES_PATH = r'D:\PythonWorkspace\operator_kayoko\examples\fastapi\web-dictaphone'

app = FastAPI()

# 정적 파일 제공
app.mount("/scripts", StaticFiles(directory=f"{TEMPLATES_PATH}/scripts"), name="scripts")
app.mount("/styles", StaticFiles(directory=f"{TEMPLATES_PATH}/styles"), name="styles")
app.mount("/app-icons", StaticFiles(directory=f"{TEMPLATES_PATH}/app-icons"), name="app-icons")

templates = Jinja2Templates(directory=TEMPLATES_PATH)

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="59.26.248.46", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    