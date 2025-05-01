import cv2
import numpy as np

net = cv2.dnn.readNetFromCaffe('dnn_models/deploy.prototxt.txt', 'dnn_models/res10_300x300_ssd_iter_140000.caffemodel')
if net.empty():
    raise RuntimeError("❌ DNN model failed to load. Check paths and file integrity.")

def detect_faces_dnn(frame):
    h, w = frame.shape[:2]
    resized_frame = cv2.resize(frame, (300, 300))
    blob = cv2.dnn.blobFromImage(resized_frame, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=True)
    net.setInput(blob)

    try:
        detections = net.forward()
    except cv2.error as e:
        print(f"Error during forward pass: {e}")
        return [], []

    faces, scores = [], []
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence > 0.6:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype("int")
            faces.append((x1, y1, x2 - x1, y2 - y1))
            scores.append(confidence)

    return faces, scores
