import cv2
import threading
import os
import atexit
from .utils import detect_faces_dnn
from .globals import camera_list, cameras, face_data, camera_locks, stream_threads, streaming_flags

snapshot_taken = False


def cleanup():
    for camera_id, camera in cameras.items():
        if camera.isOpened():
            camera.release()
    cv2.destroyAllWindows()

atexit.register(cleanup)

# Function to process and stream frames from each camera
def get_camera_stream(camera_id):
    global snapshot_taken
    streaming_flags[camera_id] = True  # Mark thread as running
    cap = cameras[camera_id]
    face_data[camera_id] = {"count": 0, "confidences": [], "snapshots": []}

    while streaming_flags.get(camera_id, False):
        success, frame = cap.read()
        if not success or frame is None:
            break

        faces, confidence_scores = detect_faces_dnn(frame)
        face_data[camera_id]["count"] = len(faces)
        face_data[camera_id]["confidences"] = [round(c * 100, 2) for c in confidence_scores]

        height, width = frame.shape[:2]

        for (x, y, w, h), confidence in zip(faces, confidence_scores):
            # Validate bounding box values
            try:
                x1, y1 = max(0, int(x)), max(0, int(y))
                x2, y2 = min(width, x1 + int(w)), min(height, y1 + int(h))

                if (x2 - x1 <= 0) or (y2 - y1 <= 0):
                    continue  # Skip invalid boxes

                # Snapshot logic
                if not snapshot_taken:
                    face_img = frame[y1:y2, x1:x2]
                    if face_img.size != 0:
                        snapshot_path = os.path.join(os.getcwd(), 'app', 'static', 'snapshots', f'{camera_id}_snapshot.jpg')
                        cv2.imwrite(snapshot_path, face_img)
                        snapshot_taken = True

                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (25, 25, 255), 2)
                percentage = confidence * 100
                text = f"{percentage:.2f}%"
                y_text = y1 - 10 if y1 - 10 > 10 else y1 + 10
                cv2.putText(frame, text, (x1, y_text), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 25, 255), 2)

            except Exception as e:
                print(f"[Error] Drawing face box: {e}")
                continue

        # Encode frame to JPEG for streaming
        try:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"[Error] Streaming frame: {e}")
            break

# Function to handle face count dynamically for each camera
def get_face_count(camera_id):
    try:
        camera_info = camera_list[camera_id]
        cap = cv2.VideoCapture(camera_info['source'])

        success, frame = cap.read()
        if not success or frame is None:
            return {"error": "Failed to capture frame from camera."}, 500

        faces, confidences = detect_faces_dnn(frame)

        if faces is None or confidences is None:
            return {"error": "Face detection failed."}, 500

        percentages = [round(c * 100, 2) for c in confidences]

        return {
            "face_count": len(faces),
            "confidences": percentages
        }, 200

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500


# Function to refresh a specific camera feed
def refresh_camera_feed(camera_id):
    try:
        with camera_locks[camera_id]:
            if cameras[camera_id].isOpened():
                cameras[camera_id].release()
            cameras[camera_id] = cv2.VideoCapture(camera_list[camera_id]['source'], cv2.CAP_PROP_BUFFERSIZE)
            if not cameras[camera_id].isOpened():
                return f"Failed to reopen {camera_id} camera", 500
        return f"{camera_id} camera refreshed", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

# Function to handle each camera stream
def handle_camera_stream(camera_id):
    for frame in get_camera_stream(camera_id):
        pass  # Handle the frame as needed (send to frontend or process further)

