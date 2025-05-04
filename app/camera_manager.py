# camera_manager.py
import threading
from app.globals import streaming_flags, stream_threads
from app.camera import get_camera_stream

def stop_camera_stream(camera_id):
    streaming_flags[camera_id] = False
    # Check if the thread exists and is alive before attempting to join
    if camera_id in stream_threads and stream_threads[camera_id] is not None:
        if stream_threads[camera_id].is_alive():
            stream_threads[camera_id].join()
        stream_threads[camera_id] = None  # Reset the thread after stopping


def start_camera_stream(camera_id):
    stop_camera_stream(camera_id)
    streaming_flags[camera_id] = True
    thread = threading.Thread(target=get_camera_stream, args=(camera_id,))
    thread.start()
    stream_threads[camera_id] = thread
