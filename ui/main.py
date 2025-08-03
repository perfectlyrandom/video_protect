from nicegui import ui
import httpx
import os
from pathlib import Path
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"  # Default FastAPI URL
UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True, parents=True)

class VideoProcessorUI:
    def __init__(self):
        self.file_path: Optional[str] = None
        self.file_name: Optional[str] = None
        self.duration: Optional[float] = None
        self.processed_url: Optional[str] = None
        self.file_id: Optional[str] = None
        self.status_label: Optional[ui.label] = None
        self.process_btn: Optional[ui.button] = None
        self.upload: Optional[ui.upload] = None
        self.video: Optional[ui.video] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        with ui.header(elevated=True).style('background-color: #1e88e5').classes('items-center justify-between'):
            ui.label('Video Protect').classes('text-h5')
            ui.button('GitHub', on_click=lambda: ui.open('https://github.com/perfectlyrandom/video_protect'))
        
        # Main content
        with ui.card().classes('w-full max-w-3xl mx-auto mt-8'):
            ui.label('Upload Video').classes('text-h6')
            
            # File upload
            with ui.row().classes('w-full items-center'):
                self.upload = ui.upload(
                    label='Choose a video file',
                    on_upload=self.handle_upload,
                    max_file_size=100_000_000  # 100MB limit
                ).props('accept=video/*').classes('w-64')
                
                self.process_btn = ui.button(
                    'Process Video',
                    on_click=self.process_video,
                    color='primary'
                ).props('disable')
            
            # Video info
            with ui.column().bind_visibility_from(self, 'file_name'):
                ui.separator()
                with ui.row().classes('w-full'):
                    ui.label('File:').classes('font-bold')
                    ui.label().bind_text_from(self, 'file_name')
                
                with ui.row().classes('w-full'):
                    ui.label('Status:').classes('font-bold')
                    self.status_label = ui.label('Ready to process')
            
            # Processed video preview
            with ui.column().bind_visibility_from(self, 'processed_url'):
                ui.separator()
                ui.label('Processed Video').classes('text-h6')
                self.video = ui.video('').props('controls')
                self.video.bind_source_from(self, 'processed_url')
                
                with ui.row():
                    ui.button('Download', on_click=self.download_video, icon='download')
        
        # Status bar
        self.status = ui.label().classes('text-center text-grey-8 mt-4')
        
    async def handle_upload(self, event):
        print('DEBUG: handle_upload called')
        try:
            self.file_path = os.path.join(UPLOAD_FOLDER, event.name)
            self.file_name = event.name
            self.duration = None
            self.processed_url = None
            self.file_id = None

            content = event.content
            if isinstance(content, bytes):
                with open(self.file_path, 'wb') as f:
                    f.write(content)
            elif hasattr(content, 'read'):
                with open(self.file_path, 'wb') as f:
                    f.write(content.read())
            else:
                raise ValueError("Unsupported file content type")
            print('DEBUG: File saved to', self.file_path)

            self.process_btn.props(remove='disable')
            print('DEBUG: Process button enabled')
            self.status_label.text = f'File uploaded: {self.file_name}. Ready to process.'
            self.status_label.classes(remove='text-negative')
        except Exception as e:
            print(f'DEBUG: Exception in handle_upload: {e}')
            self.status_label.text = f'Error: {str(e)}'
            self.status_label.classes('text-negative')
    
    async def process_video(self):
        """Send video to backend for processing"""
        if not self.file_path:
            self.status_label.text = 'No file selected'
            return
            
        self.status_label.text = 'Processing video...'
        self.process_btn.props('disable')
        
        try:
            # 1. Upload the file
            with open(self.file_path, 'rb') as f:
                files = {'file': (self.file_name, f, 'video/mp4')}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{API_BASE_URL}/upload/",
                        files=files
                    )
                    response.raise_for_status()
                    data = response.json()
                    self.file_id = data['file_id']
            
            # 2. Process the video
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE_URL}/process/{self.file_id}")
                response.raise_for_status()
                data = response.json()
                self.duration = data['duration']
                self.processed_url = f"{API_BASE_URL}/download/{self.file_id}"
                
            self.status_label.text = 'Processing complete!'
            
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
            self.status_label.classes('text-negative')
        finally:
            self.process_btn.props(remove='disable')
    
    async def download_video(self):
        """Download the processed video"""
        if not self.processed_url:
            return
            
        ui.download(self.processed_url, self.file_name or 'processed_video.mp4')

# Create the app instance
app = VideoProcessorUI()

# This allows the file to be run directly
if __name__ == '__main__':
    ui.run(title="Video Protect", port=8080, reload=False)

# Export the UI for use in run.py
ui_instance = ui
