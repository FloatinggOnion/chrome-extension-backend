from fastapi import FastAPI, status, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio

from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
import speech_recognition as sr


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
video_buffer = bytearray()

# Concurrency
executor = ThreadPoolExecutor()

# Initialize a recognizer
recognizer = sr.Recognizer()

# Get health
app.get('/health')
async def get_health():
    return status.HTTP_200_OK


# # Stream video
# @app.post('/stream')
# async def stream_video(chunk: bytes):
#     global video_buffer
#     video_buffer.extend(chunk)
    
#     return {
#         "message": "Chunk received successfully",
#         "code": status.HTTP_202_ACCEPTED
#     }


# Stream video
@app.websocket('/ws')
async def stream_video(websocket: WebSocket):
    global video_buffer

    await websocket.accept()

    while True:
        await asyncio.sleep(0.1)
        chunk = await websocket.receive_bytes()
        video_buffer.extend(chunk)
        

        with open(record_path / "recorded_video.mp4", "wb") as f:
            f.write(video_buffer)

        audio_path = "recorded_audio.wav"
        with open(audio_path, "wb") as audio_file:
            audio_file.write(video_buffer)


        def transcribe_audio():
            nonlocal audio_path
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                try:
                    transcription = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    transcription = "Could not understand audio"
                except sr.RequestError:
                    transcription = "Could not request results; check network connection"
            return transcription
        
        # Start audio transcription in a separate thread
        caption = executor.submit(transcribe_audio)

        await websocket.send_bytes(video_buffer, caption)

        video_buffer = bytearray()  # Reset buffer after saving
    
        # return {
        #     "message": "Chunk received successfully",
        #     "code": status.HTTP_202_ACCEPTED
        # }


# Define route to save video to disk
@app.post("/save/")
async def save_video():
    global video_buffer
    with open(record_path / "recorded_video.mp4", "wb") as f:
        f.write(video_buffer)

    audio_path = "recorded_audio.wav"
    with open(audio_path, "wb") as audio_file:
        audio_file.write(video_buffer)


    def transcribe_audio():
        nonlocal audio_path
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                transcription = "Could not understand audio"
            except sr.RequestError:
                transcription = "Could not request results; check network connection"
        return transcription
    
     # Start audio transcription in a separate thread
    caption = executor.submit(transcribe_audio)

    video_buffer = bytearray()  # Reset buffer after saving
    return {
        "message": "Video saved successfully",
        "code": status.HTTP_201_CREATED,
        "transcription": caption.result()
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