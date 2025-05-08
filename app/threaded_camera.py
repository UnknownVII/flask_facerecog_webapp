import cv2
import time
import threading
from imutils.video import VideoStream

class ThreadedCamera:
    def __init__(self, src=0, use_videostream=False, fps=120):
        self.src = src
        self.fps = fps
        self.frame = None
        self.status = False
        self.use_videostream = use_videostream
        self.lock = threading.Lock()
        self.running = True

        if self.use_videostream:
            self.capture = VideoStream(src=self.src).start()
        else:
            self.capture = cv2.VideoCapture(self.src)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.use_videostream:
                frame = self.capture.read()
                status = frame is not None
            else:
                # Drop stale frames (buffersize should already help)
                self.capture.grab()
                status, frame = self.capture.read()

            with self.lock:
                self.status = status
                self.frame = frame

            if not self.use_videostream:
                time.sleep(1 / self.fps)

    def read(self):
        with self.lock:
            return self.status, self.frame.copy() if self.frame is not None else None

    def release(self):
        self.running = False
        self.thread.join(timeout=2)

        if self.use_videostream:
            self.capture.stop()
        else:
            self.capture.release()
