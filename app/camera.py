import cv2
import atexit
import app.cache as cache
from app.models import is_similar, store_embedding
from .face_recognizer import face_app

from .globals import cameras, face_data, streaming_flags, skip_detection_flags

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

        high_res_frame = frame.copy()
        display_frame = cv2.resize(frame, (320, 180))

        if skip_detection_flags.get(camera_id, False):
            try:
                ret, buffer = cv2.imencode('.jpg', display_frame)
                if ret:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                continue  # Skip face detection
            except Exception as e:
                print(f"[Stream Skip Error] {e}")
                break

        try:
            rgb_frame = cv2.cvtColor(high_res_frame, cv2.COLOR_BGR2RGB)
            results = face_app.get(rgb_frame)
        except Exception as e:
            print(f"[FaceAnalysis Error] {e}")
            continue

        face_data[camera_id]["count"] = len(results)
        face_data[camera_id]["confidences"] = [round(face.det_score * 100, 2) for face in results]

        height, width = high_res_frame.shape[:2]
        for face in results:
            try:
                x1, y1, x2, y2 = face.bbox.astype(int)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)

                if x2 - x1 <= 0 or y2 - y1 <= 0:
                    continue

                face_img = high_res_frame[y1:y2, x1:x2]
                embedding = face.embedding
                matched_name = None
                color = (0, 0, 255)

                if embedding is not None and cache.embedding_cache:
                    found_match = False
                    for record in cache.embedding_cache:
                        record_name = record["name"]
                        cached_emb = record["embedding"]

                        if is_similar(embedding, cached_emb):
                            found_match = True
                            if record_name and record_name.lower() != "unknown":
                                matched_name = record_name
                                color = (0, 255, 0)
                            break  # Stop after first match

                    if not found_match:
                        store_embedding(camera_id, embedding, face_img, name="Unknown")

                # Scale box coordinates to match display frame resolution
                scale_x = 320 / width
                scale_y = 180 / height
                dx1, dy1 = int(x1 * scale_x), int(y1 * scale_y)
                dx2, dy2 = int(x2 * scale_x), int(y2 * scale_y)

                cv2.rectangle(display_frame, (dx1, dy1), (dx2, dy2), color, 2)
                label = f""
                y_text = dy1 - 10 if dy1 - 10 > 10 else dy1 + 10
                cv2.putText(display_frame, label, (dx1, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

            except Exception as e:
                print(f"[Draw Error] {e}")

        try:
            ret, buffer = cv2.imencode('.jpg', display_frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[Stream Error] {e}")
            break

def cleanup():
    for cam_id, cam in cameras.items():
        print(f"Releasing camera {cam_id}")
        cam.release()
    cv2.destroyAllWindows()

atexit.register(cleanup)