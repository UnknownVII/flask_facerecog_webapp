# app/__init__.py
from flask import Flask
from .routes import main  # Import the Blueprint
import os

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join("app", "static")
    )
    # Set up a static folder for the snapshots
    # Register the Blueprint
    app.register_blueprint(main)

    return app

# from flask import Flask, render_template, Response, send_file, make_response
# import cv2
# import numpy as np
# import os
# import atexit  # For cleanup at shutdown
# import threading

# app = Flask(__name__)
# camera_lock = threading.Lock()

# # Load the DNN model (Caffe)
# net = cv2.dnn.readNetFromCaffe('deploy.prototxt.txt', 'res10_300x300_ssd_iter_140000.caffemodel')
# if net.empty():
#     raise RuntimeError("❌ DNN model failed to load. Check paths and file integrity.")

# camera = cv2.VideoCapture(0)

# snapshot_taken = False  # To capture only once

# # Register cleanup function to release the camera when the app shuts down
# def cleanup():
#     if camera.isOpened():
#         camera.release()
#     cv2.destroyAllWindows()

# atexit.register(cleanup)

# def gen_frames():
#     global snapshot_taken
#     while True:
#         with camera_lock:
#             success, frame = camera.read()
#         if not success:
#             break
#         else:
#             faces, confidence_scores = detect_faces_dnn(frame)
#             for (x, y, w, h), confidence in zip(faces, confidence_scores):
#                 # Save only the face area if snapshot hasn't been taken
#                 if not snapshot_taken:
#                     face_img = frame[y:y+h, x:x+w]  # Crop the face
#                     cv2.imwrite("snapshot.jpg", face_img)
#                     snapshot_taken = True

#                 # Draw red rectangle for display only
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

#                 # Display the confidence score as percentage
#                 confidence_percentage = confidence * 100  # Multiply by 100 to convert to percentage
#                 text = f"{confidence_percentage:.2f}%"  # Format as percentage
#                 y = y - 10 if y - 10 > 10 else y + 10
#                 cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# def detect_faces_dnn(frame):
#     # Get the height and width of the frame
#     h, w = frame.shape[:2]

#     # Resize the frame to the required 300x300 size
#     resized_frame = cv2.resize(frame, (300, 300))

#     # Create a blob from the resized frame
#     blob = cv2.dnn.blobFromImage(resized_frame, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=True)

#     # Set the input for the network
#     net.setInput(blob)
    
#     # Perform forward pass
#     try:
#         detections = net.forward()
#     except cv2.error as e:
#         print(f"Error during forward pass: {e}")
#         return [], []  # Return empty lists if an error occurs

#     faces = []
#     confidence_scores = []  # Create a list to store confidence scores

#     for i in range(0, detections.shape[2]):
#         confidence = float(detections[0, 0, i, 2])  # Convert to regular Python float

#         # Filter out weak detections
#         if confidence > 0.6:
#             box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#             (x1, y1, x2, y2) = box.astype("int")
#             faces.append((x1, y1, x2 - x1, y2 - y1))
#             confidence_scores.append(confidence)  # Store the confidence value

#     return faces, confidence_scores  # Return both faces and their confidence scores


# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/snapshot')
# def snapshot():
#     if os.path.exists("snapshot.jpg"):
#         response = make_response(send_file("snapshot.jpg", mimetype='image/jpeg'))
#         response.headers['Cache-Control'] = 'no-store'
#         return response
#     else:
#         return "No snapshot yet", 404

# @app.route('/reset_snapshot')
# def reset_snapshot():
#     global snapshot_taken
#     snapshot_taken = False
#     return "Snapshot reset", 200

# @app.route('/face_count')
# def face_count():
#     with camera_lock:
#         success, frame = camera.read()
#     if not success:
#         return "Failed to capture frame", 500
#     faces, confidences = detect_faces_dnn(frame)
#     # Convert to percentage and round to 2 decimal places
#     confidence_percentage = [round(c * 100, 2) for c in confidences]
#     return {"face_count": len(faces), "confidences": confidence_percentage }

# @app.route('/refresh_camera')
# def refresh_camera():
#     global camera
#     try:
#         with camera_lock:
#             if camera.isOpened():
#                 camera.release()
#             camera = cv2.VideoCapture(0)
#             if not camera.isOpened():
#                 return "Failed to reopen camera", 500
#         return "Camera refreshed", 200
#     except Exception as e:
#         return f"Error: {str(e)}", 500
    
# @atexit.register
# def cleanup():
#     if camera.isOpened():
#         camera.release()
#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)