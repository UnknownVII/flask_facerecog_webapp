import threading
import cv2
from app.models import get_all_working_cameras
from app.threaded_camera import ThreadedCamera

camera_rows = get_all_working_cameras()
camera_refresh_lock = threading.Lock()
camera_list = {
    f"cam_{cam[0]}": {"source": cam[2], "name": cam[1]}
    for cam in camera_rows
}

# camera_list = {
#     "webcam": {"source": 0, "name": "Built-in Webcam"}
# }

face_data = {}
camera_locks = {camera_id: threading.Lock() for camera_id in camera_list}
cameras = {camera_id: ThreadedCamera(info['source']) for camera_id, info in camera_list.items()}
streaming_flags = {}
stream_threads = {}

def reload_camera_data():
    from app.camera_manager import stop_camera_stream, start_camera_stream
    global camera_list, camera_locks, cameras, streaming_flags, stream_threads

    # Stop all current camera streams
    for camera_id in list(streaming_flags.keys()):
        stop_camera_stream(camera_id)

    # Release all old camera resources
    for cap in cameras.values():
        cap.release()

    # Fetch updated camera rows
    camera_rows = get_all_working_cameras()

    # Clear and rebuild globals
    camera_list.clear()
    camera_locks.clear()
    cameras.clear()
    streaming_flags.clear()
    stream_threads.clear()

    for cam in camera_rows:
        cam_id = f"cam_{cam[0]}"
        source = cam[2]
        camera_list[cam_id] = {"source": source, "name": cam[1]}
        camera_locks[cam_id] = threading.Lock()
        cameras[cam_id] = cv2.VideoCapture(source)
        streaming_flags[cam_id] = False
        stream_threads[cam_id] = None

    # Start fresh camera streams
    for camera_id in camera_list:
        start_camera_stream(camera_id)


