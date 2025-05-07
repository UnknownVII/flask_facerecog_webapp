import cv2
import os
import atexit
from multiprocessing import Process, Queue
from app.models import get_all_embeddings, is_similar, store_embedding
from .face_recognizer import face_app

from .globals import camera_list, cameras, face_data, streaming_flags

# snapshot_taken = False
frame_queues = {}
streaming_threads = {}

# Function to process and stream frames from each camera
def get_camera_stream(camera_id):
    streaming_flags[camera_id] = True
    cam = cameras[camera_id]
    face_data[camera_id] = {"count": 0, "confidences": [], "snapshots": []}

    while streaming_flags.get(camera_id, False):
        success, frame = cam.read()
        if not success or frame is None:
            continue

        # Convert to RGB once
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            results = face_app.get(rgb_frame)
        except Exception as e:
            print(f"[FaceAnalysis Error] {e}")
            continue

        face_data[camera_id]["count"] = len(results)
        face_data[camera_id]["confidences"] = [round(face.det_score * 100, 2) for face in results]

        height, width = frame.shape[:2]
        for face in results:
            try:
                x1, y1, x2, y2 = face.bbox.astype(int)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)

                if x2 - x1 <= 0 or y2 - y1 <= 0:
                    continue

                face_img = frame[y1:y2, x1:x2]
                embedding = face.embedding
                # conf = float(face.det_score)
                matched_name = None
                color = (0, 0, 255)  # red by default

                if embedding is not None:
                    for record in get_all_embeddings():
                        name = record["name"]
                        cached_emb = record["embedding"]
                        if is_similar(embedding, cached_emb):
                            matched_name = name
                            color = (0, 255, 0)  # green if known
                            break
                    if not matched_name:
                        matched_name = "Unknown"

                store_embedding(camera_id, embedding, name)
                # Save snapshot unconditionally if available
                if face_img.size:
                    snapshot_path = os.path.join("app", "static", "snapshots", f"{camera_id}_snapshot.jpg")
                    cv2.imwrite(snapshot_path, face_img)

                # Draw box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 5)
                # label = f"{matched_name} - {conf * 100:.2f}%"
                label = f""
                y_text = y1 - 10 if y1 - 10 > 10 else y1 + 10
                cv2.putText(frame, label, (x1, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            except Exception as e:
                print(f"[Draw Error] {e}")

        try:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[Stream Error] {e}")
            break


# Function to handle face count dynamically for each camera
def get_face_count(camera_id):
    try:
        camera_info = camera_list[camera_id]
        cap = cv2.VideoCapture(camera_info['source'])

        success, frame = cap.read()
        if not success or frame is None:
            return {"error": "Failed to capture frame from camera."}, 500

        # Convert frame to RGB as InsightFace expects RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Use InsightFace for face detection
        faces = face_app.get(rgb_frame)

        if not faces:
            return {"error": "Face detection failed."}, 500

        # Get the number of detected faces and their confidence scores
        face_count = len(faces)
        confidences = [round(face.score * 100, 2) for face in faces]

        return {
            "face_count": face_count,
            "confidences": confidences
        }, 200

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500

def cleanup():
    for cam_id, cam in cameras.items():
        print(f"Releasing camera {cam_id}")
        cam.release()
    cv2.destroyAllWindows()

atexit.register(cleanup)