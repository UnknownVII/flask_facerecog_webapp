import cv2
import numpy as np
import re
from flask import flash
from .models import set_camera_status



def detect_faces_dnn(frame):
    net = cv2.dnn.readNetFromCaffe('dnn_models/deploy.prototxt.txt', 'dnn_models/res10_300x300_ssd_iter_140000.caffemodel')
    if net.empty():
        raise RuntimeError("DNN model failed to load. Check paths and file integrity.")
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    h, w = frame.shape[:2]
    resized_frame = cv2.resize(frame, (300, 300))
    blob = cv2.dnn.blobFromImage(
        resized_frame, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=True
    )
    net.setInput(blob)

    try:
        detections = net.forward()
    except cv2.error as e:
        print(f"Error during forward pass: {e}")
        return [], []

    faces, scores = [], []

    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < 0.5:  # Raise threshold to reduce false positives
            continue

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        if not np.isfinite(box).all():
            continue

        x1, y1, x2, y2 = box.astype("int")

        # Sanity check box coordinates
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)

        if x2 <= x1 or y2 <= y1:
            continue

        width, height = x2 - x1, y2 - y1
        if width < 20 or height < 20:  # filter tiny "faces"
            continue

        faces.append((x1, y1, width, height))
        scores.append(confidence)

    return faces, scores

def validate_rtsp(rtsp_url, camera_id):
    cap = cv2.VideoCapture(rtsp_url)
    ret, _ = cap.read()
    cap.release()
    set_camera_status(camera_id, int(ret))
    return ret

def is_valid_ip(ip):
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return re.match(pattern, ip) is not None and all(0 <= int(part) <= 255 for part in ip.split("."))


