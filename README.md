# chrome-extension-backend
The backend serving a screen recording api

### Enpoints
- GET `/health/`: Check health of the api
- POST `/upload/`: Upload a video
- GET `/videos/`: Get all videos
- GET `/videos/{filename}`: Get a specific video
- DELETE `/videos/{filename}`: Delete a video