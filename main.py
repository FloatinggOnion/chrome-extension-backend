from fastapi import FastAPI, status, HTTPException
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

# Buffer for video data
vid_buff = bytearray()

# Get health
app.get('/health')
async def get_health():
    return status.HTTP_200_OK


# Stream video
@app.post('/stream')
async def stream_video(chunk: bytes):
    global vid_buff
    vid_buff.extend(chunk)
    
    return {
        "message": "Chunk received successfully",
        "code": status.HTTP_202_ACCEPTED
    }


# Define route to save video to disk
@app.post("/save/")
async def save_video():
    global video_buffer
    with open(record_path / "recorded_video.mp4", "wb") as f:
        f.write(video_buffer)
    video_buffer = bytearray()  # Reset buffer after saving
    return {
        "message": "Video saved successfully",
        "code": status.HTTP_201_CREATED,
        }


# # Get specific video
# @app.get('/videos/{filename}')
# async def get_video(filename: str):
#     try:
#         video = record_path / filename
#         return {
#             "filename": video.name,
#             "path": str(video),
#             "size": video.stat().st_size
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error getting video: {str(e)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)