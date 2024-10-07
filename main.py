from fastapi import FastAPI, UploadFile, File, Form
from test import process_file_and_text
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://192.168.29.147:3000",  # replace with your own ipv4 address:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Route for uploading only files (file is now required)
@app.post("/fileUpload")
async def upload_file_route(file: UploadFile = File(...)):
    files_content = await file.read()
    result = process_file_and_text(files_content, file.filename, "")
    return result


# Route for submitting only text (description is now required)
@app.post("/text")
async def submit_text_route(description: str = Form(...)):  # Text is now required
    result = process_file_and_text(b"", "", description)
    return result


# Route for submitting both file and text (both are required)
@app.post("/file_and_text")
async def upload_file_and_text_route(
    file: UploadFile = File(...),  # File is now required
    description: str = Form(...),  # Text is now required
):
    files_content = await file.read()
    result = process_file_and_text(files_content, file.filename, description)
    return result
