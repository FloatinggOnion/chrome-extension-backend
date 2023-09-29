from fastapi import FastAPI, status, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path


app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve files to the frontend
app.mount('/', StaticFiles(directory='/', html=True))

# Recordings storage path
record_path = Path('recordings')
record_path.mkdir(parents=True, exist_ok=True)

# Get health
app.get('/health')
async def get_health():
    return status.HTTP_200_OK

# Upload video
@app.post('/upload')
async def upload_video(video: UploadFile = File(...)):
    try:
        with open(record_path / video.filename, "wb") as f:
            f.write(video.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving video: {str(e)}")
    return {
        "message": "Video uploaded successfully",
        "filename": video.filename,
        "path": str(record_path / video.filename),
        "code": status.HTTP_201_CREATED
        }

# Get specific video
@app.get('/videos/{filename}')
async def get_video(filename: str):
    try:
        video = record_path / filename
        return {
            "filename": video.name,
            "path": str(video),
            "size": video.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting video: {str(e)}")

# Get all videos
@app.get('/videos')
async def get_videos():
    videos = []
    for video in record_path.iterdir():
        videos.append({
            "filename": video.name,
            "path": str(video),
            "size": video.stat().st_size
        })
    return videos

# Delete video
@app.delete('/videos/{filename}')
async def delete_video(filename: str):
    try:
        (record_path / filename).unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")
    return {
        "message": "Video deleted successfully",
        "filename": filename,
        "code": status.HTTP_200_OK
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)