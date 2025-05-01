import cv2
import threading
import atexit
import os
from .utils import detect_faces_dnn

camera = cv2.VideoCapture(0)
camera_lock = threading.Lock()
snapshot_taken = False

def cleanup():
    with camera_lock:
        if camera.isOpened():
            camera.release()
        cv2.destroyAllWindows()

atexit.register(cleanup)

def gen_frames():
    global snapshot_taken
    while True:
        with camera_lock:
            success, frame = camera.read()
        if not success:
            break

        faces, confidence_scores = detect_faces_dnn(frame)
        for (x, y, w, h), confidence in zip(faces, confidence_scores):
            if not snapshot_taken:
                face_img = frame[y:y+h, x:x+w]
                snapshot_path = os.path.join(os.getcwd(), 'app', 'static', 'snapshots', 'snapshot.jpg')
                cv2.imwrite(snapshot_path, face_img)
                print(f"Saving snapshot to: {snapshot_path}")
                snapshot_taken = True

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            percentage = confidence * 100
            text = f"{percentage:.2f}%"
            y_text = y - 10 if y - 10 > 10 else y + 10
            cv2.putText(frame, text, (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def take_snapshot():
    global snapshot_taken
    snapshot_taken = True

def reset_snapshot():
    global snapshot_taken
    snapshot_taken = False

def get_face_count():
    with camera_lock:
        success, frame = camera.read()
    if not success:
        return "Failed to capture frame", 500
    faces, confidences = detect_faces_dnn(frame)
    percentages = [round(c * 100, 2) for c in confidences]
    return {"face_count": len(faces), "confidences": percentages}

def refresh_camera_feed():
    global camera
    try:
        with camera_lock:
            if camera.isOpened():
                camera.release()
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return "Failed to reopen camera", 500
        return "Camera refreshed", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
