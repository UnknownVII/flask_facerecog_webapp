# Flask OpenCV Snapshot App

This project is a simple Flask app that integrates OpenCV to stream video from your webcam, take snapshots, and count detected faces in real time.

## Features

- Live webcam video feed using OpenCV.
- Snapshot capture and save to a static folder.
- Route to display latest snapshot (`/snapshot`).
- Face detection and face count display via `/face_count` endpoint.
- Auto-refreshing image via timestamped query string.
- Clean snapshot route with cache-busting and 404 fallback.
- Snapshot stored at `app/static/snapshots/snapshot.jpg`.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/opencv-flask.git
cd opencv-flask
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python run.py
```

## Routes

- `/` — Home page with video stream and snapshot controls.
- `/video_feed` — MJPEG video stream.
- `/snapshot` — Displays last snapshot taken.
- `/face_count` — Returns current face count in JSON.
- `/reset_snapshot` — Clears snapshot (resets file).

## Notes

- Snapshots are saved in `app/static/snapshots/`.
- Images are served via `/snapshot` using `send_file` with `Cache-Control: no-store` to force fresh loads.
- If no snapshot exists, a 404 is returned.
- This setup is for local development only — do not expose webcam apps without securing routes.
