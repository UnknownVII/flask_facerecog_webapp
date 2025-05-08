from app.models import get_all_working_cameras
from app.threaded_camera import ThreadedCamera
import threading

camera_list = {}
camera_locks = {}
cameras = {}
streaming_flags = {}
stream_threads = {}
face_data = {}
camera_refresh_lock = threading.Lock()

def reload_camera_data():
    from app.camera_manager import stop_camera_stream, start_camera_stream
    global camera_list, camera_locks, cameras, streaming_flags, stream_threads

    print("[INFO] Reloading camera data...")

    # Stop all current camera streams
    for camera_id in list(streaming_flags.keys()):
        stop_camera_stream(camera_id)

    # Release all old camera resources
    for cap in cameras.values():
        if cap:
            cap.release()

    # Fetch new camera rows from DB
    camera_rows = get_all_working_cameras()

    # Clear current globals
    camera_list.clear()
    camera_locks.clear()
    cameras.clear()
    streaming_flags.clear()
    stream_threads.clear()

    if not camera_rows:
        print("[WARN] No cameras found in database. Using debug fallback configuration.")

        camera_list.update({
            "webcam": {"source": 0, "name": "Phone Webcam"},
            # "webcam2": {"source": 1, "name": "Built-in Webcam"},
            # "tapo": {"source":"rtsp://admin_face_recog:pehtak-mywbyw-4doRko@192.168.100.88/stream1", "name": "Tapo"},
        })

    else:
        for cam in camera_rows:
            cam_id = f"cam_{cam[0]}"
            source = cam[2]
            camera_list[cam_id] = {"source": source, "name": cam[1]}

    for camera_id, info in camera_list.items():
        camera_locks[camera_id] = threading.Lock()
        cameras[camera_id] = ThreadedCamera(info['source'], use_videostream=False)
        streaming_flags[camera_id] = False
        stream_threads[camera_id] = None

    # Start camera streams
    for camera_id in camera_list:
        start_camera_stream(camera_id)

    print(f"[INFO] Loaded {len(camera_list)} camera(s).")
