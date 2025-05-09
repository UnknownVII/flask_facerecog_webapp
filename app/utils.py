import cv2
import re
from .models import set_camera_status

def validate_rtsp(rtsp_url, camera_id):
    cap = cv2.VideoCapture(rtsp_url)
    ret, _ = cap.read()
    cap.release()
    set_camera_status(camera_id, int(ret))
    return ret

def is_valid_ip(ip):
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return re.match(pattern, ip) is not None and all(0 <= int(part) <= 255 for part in ip.split("."))
