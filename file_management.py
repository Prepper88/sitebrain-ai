import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

UPLOAD_DIR = "docs/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

# Allowed file extensions
ALLOWED_EXT = {"pdf", "txt", "docx"}


def allowed(filename: str):
    return filename.split(".")[-1].lower() in ALLOWED_EXT


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not allowed(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    return {"name": file.filename, "size": os.path.getsize(filepath), "url": f"/files/view/{file.filename}"}


@router.get("/list")
async def list_files():
    files = []
    for fn in os.listdir(UPLOAD_DIR):
        full = os.path.join(UPLOAD_DIR, fn)
        if os.path.isfile(full):
            files.append({
                "name": fn,
                "size": os.path.getsize(full),
                "url": f"/api/files/view/{fn}"
            })
    return files


@router.get("/view/{filename}")
async def view_file(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    # Stream directly (works for PDFs)
    media_type = "application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(filepath, media_type=media_type)


@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(filepath)
    return {"deleted": filename}
