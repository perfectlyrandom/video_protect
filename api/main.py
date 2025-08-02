from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import VideoFileClip
import os
from typing import Optional
import uuid

app = FastAPI(title="Video Processing API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_video(file: UploadFile):
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi')):
        raise HTTPException(status_code=400, detail="Only video files are allowed")
    
    # Save the uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"file_id": file_id, "original_filename": file.filename}

@app.get("/process/{file_id}")
async def process_video(file_id: str, resolution: Optional[str] = "480p"):
    # Find the file with the given ID
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(file_id)]
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    
    input_path = os.path.join(UPLOAD_DIR, files[0])
    output_path = os.path.join(PROCESSED_DIR, f"{file_id}_processed.mp4")
    
    try:
        # Get video duration
        with VideoFileClip(input_path) as video:
            duration = video.duration
            
            # Downsample the video
            if resolution == "720p":
                video_resized = video.resize(height=720)
            elif resolution == "480p":
                video_resized = video.resize(height=480)
            elif resolution == "360p":
                video_resized = video.resize(height=360)
            else:
                video_resized = video
            
            # Save the processed video
            video_resized.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
        
        return {
            "status": "success",
            "original_duration": duration,
            "processed_file": f"/download/{file_id}_processed.mp4"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
