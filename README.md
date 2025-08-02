# Video Protect

A FastAPI backend with a NiceGUI frontend for processing and protecting videos.

## Features

- Upload video files (MP4, MOV, AVI, etc.)
- Get video duration
- Process videos with different resolutions (360p, 480p, 720p)
- Simple web interface for easy interaction
- REST API for programmatic access

## Prerequisites

- Python 3.9+
- Poetry (for dependency management)
- FFmpeg (for video processing)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/perfectlyrandom/video_protect.git
   cd video_protect
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

### Virtual Environment

This project uses Poetry for dependency management. The virtual environment is created in the project directory (`.venv`) for better IDE integration and Jupyter support.

1. Configure Poetry to create the virtual environment in the project directory:
   ```bash
   poetry config virtualenvs.in-project true
   ```

2. Remove any existing virtual environment and reinstall dependencies:
   ```bash
   poetry env remove python  # Remove existing environment if any
   poetry install  # Recreate the environment and install dependencies
   ```

#### For Jupyter Notebook/Lab:

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   .\.venv\Scripts\activate  # On Windows
   ```

2. Install ipykernel if not already installed:
   ```bash
   poetry add ipykernel
   ```

3. Register the kernel with Jupyter:
   ```bash
   python -m ipykernel install --user --name=video-protect --display-name="Python (video-protect)"
   ```

4. Now you can select the "Python (video-protect)" kernel in Jupyter.

#### Verifying the Kernel:
```bash
jupyter kernelspec list
```

### FFmpeg Installation

For video processing, you'll need FFmpeg:
   - On macOS: `brew install ffmpeg`
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On Windows: Download from [FFmpeg's website](https://ffmpeg.org/download.html)

## Running the Application

### Development Setup

For development, it's recommended to run the backend and frontend in separate terminals for better error visibility and debugging.

#### 1. Start the Backend API

In the first terminal:
```bash
# From the project root directory
poetry run uvicorn api.main:app --reload
```

The backend will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

#### 2. Start the Frontend UI

In a second terminal:
```bash
# From the project root directory
poetry run python -m ui.main
```

The frontend will be available at `http://localhost:8080`

### Production Setup

For production, consider using a process manager like `systemd` or `supervisor` to manage both services, or containerize the application with Docker.

## Project Structure

```
video_protect/
├── api/                # FastAPI backend
│   └── main.py         # API endpoints
├── ui/                 # NiceGUI frontend
│   ├── __init__.py
│   ├── main.py         # UI code
│   └── static/         # Static files
├── uploads/            # Uploaded videos (created automatically)
├── processed/          # Processed videos (created automatically)
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### API Endpoints

- **POST** `/upload/`
  - Upload a video file
  - Returns: `{"file_id": "unique_id"}`

- **GET** `/process/{file_id}?resolution=480p`
  - Process the uploaded video
  - Parameters:
    - `resolution`: (optional) One of: 360p, 480p (default), 720p
  - Returns: `{"status": "success", "duration": 123.45}`

- **GET** `/download/{file_id}`
  - Download the processed video file

## License

MIT
   ```

2. Process the video:
   ```bash
   curl "http://localhost:8000/process/550e8400-e29b-41d4-a716-446655440000?resolution=480p"
   ```
   Response:
   ```json
   {
     "status": "success",
     "original_duration": 120.5,
     "processed_file": "/download/550e8400-e29b-41d4-a716-446655440000_processed.mp4"
   }
   ```

3. Download the processed video:
   ```
   http://localhost:8000/download/550e8400-e29b-41d4-a716-446655440000_processed.mp4
   ```

## Requirements

- Python 3.7+
- FFmpeg (required by MoviePy)

## License

MIT
