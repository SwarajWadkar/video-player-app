from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import re

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_youtube_id(url: str):
    """Extract YouTube video ID from standard or shortened URLs."""
    youtube_regex = (
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^\s&]+)"
    )
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "video_src": None, "is_youtube": False})

@app.post("/play", response_class=HTMLResponse)
async def play_video(
    request: Request,
    url: str = Form(""),
    upload: UploadFile = File(None)
):
    video_src = None
    is_youtube = False

    if upload and upload.filename != "":
        file_path = os.path.join(UPLOAD_DIR, upload.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        video_src = f"/static/uploads/{upload.filename}"

    elif url and url.strip():
        video_id = extract_youtube_id(url.strip())
        if video_id:
            is_youtube = True
            video_src = f"https://www.youtube.com/embed/{video_id}"
        else:
            video_src = url.strip()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "video_src": video_src,
        "is_youtube": is_youtube
    })
