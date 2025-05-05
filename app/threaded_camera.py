import cv2
import time
import threading

class ThreadedCamera:
    def __init__(self, src=0, fps=60):
        self.src = src
        self.fps = fps
        self.frame = None
        self.status = False
        self.lock = threading.Lock()

        # Force TCP transport for RTSP
        # if src.startswith("rtsp://"):
        #     self.capture = cv2.VideoCapture(
        #         f"{src}", cv2.CAP_FFMPEG
        #     )
        # else:
        self.capture = cv2.VideoCapture(src)

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 16)
        self.capture.set(cv2.CAP_PROP_FPS, fps)

        # Start background frame update thread
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                status, frame = self.capture.read()
                with self.lock:
                    self.status = status
                    self.frame = frame
            time.sleep(1 / self.fps)

    def read(self):
        with self.lock:
            return self.status, self.frame.copy() if self.frame is not None else None

    def release(self):
        self.capture.release()
