from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import VideoFileClip
import os
import sys
import traceback
import pdb
from typing import Optional
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    video = None
    video_resized = None
    try:
        logger.info(f"Processing video: {input_path}")
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Get video duration and process
        logger.info("Loading video file...")
        video = VideoFileClip(input_path)
        duration = video.duration
        logger.info(f"Video loaded. Duration: {duration} seconds")
        
        # Calculate target height based on resolution
        target_height = {
            '720p': 720,
            '480p': 480,
            '360p': 360
        }.get(resolution)
        
        if target_height:
            # Calculate new dimensions while maintaining aspect ratio
            aspect_ratio = video.size[0] / video.size[1]
            new_width = int(target_height * aspect_ratio)
            video_resized = video.resize((new_width, target_height))
        else:
            video_resized = video
        
        # Save the processed video
        video_resized.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(PROCESSED_DIR, f"temp_audio_{file_id}.m4a"),
            remove_temp=True,
            logger=None  # Disable ffmpeg output
        )
        
        return {
            "status": "success",
            "original_duration": duration,
            "processed_file": f"/download/{file_id}_processed.mp4"
        }
        
    except Exception as e:
        # Log the full error and enter debugger
        error_msg = f"Error processing video: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print("\nDEBUG: Entering post-mortem debugger...")
        _, _, tb = sys.exc_info()
        pdb.post_mortem(tb)
        
        # Clean up any partially created output file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Removed incomplete output file: {output_path}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up output file: {cleanup_error}")
                
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}. Check server logs for more details."
        )
        
    finally:
        # Close video clips to release file handles
        if video_resized is not None:
            try:
                video_resized.close()
            except:
                pass
        if video is not None:
            try:
                video.close()
            except:
                pass

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
