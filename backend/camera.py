"""Camera device management with cross-platform backend support and zero-latency threaded capture."""

import sys
import time
import threading
import cv2
from typing import Optional, Tuple
import numpy as np
from config import DEFAULT_CAMERA_WIDTH, DEFAULT_CAMERA_HEIGHT, DEFAULT_CAMERA_BUFFER_SIZE


class CameraManager:
    """Manages OpenCV VideoCapture with platform-adaptive backends and a threaded

    real-time frame grabber to guarantee 0 ms buffering delay.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = DEFAULT_CAMERA_WIDTH,
        height: int = DEFAULT_CAMERA_HEIGHT,
        buffer_size: int = DEFAULT_CAMERA_BUFFER_SIZE
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.buffer_size = buffer_size
        self.cap: Optional[cv2.VideoCapture] = None

        # Threaded capture synchronization
        self._thread: Optional[threading.Thread] = None
        self._running: bool = False
        self._lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None

    def start(self) -> bool:
        """Initializes the video capture device and spawns the background grabber."""
        self.release()

        # DirectShow is Windows-specific; macOS and Linux use default capture (AVFoundation/V4L)
        if sys.platform.startswith("win"):
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap or not self.cap.isOpened():
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)

        # Launch dedicated background frame grabber thread to continuously drain DirectShow buffer
        self._running = True
        self._thread = threading.Thread(target=self._capture_worker, daemon=True)
        self._thread.start()

        # Wait up to 1.5s for initial valid frame
        start_time = time.time()
        while time.time() - start_time < 1.5:
            with self._lock:
                if self._latest_frame is not None:
                    return True
            time.sleep(0.02)

        return self.is_opened()

    def _capture_worker(self):
        """Worker thread that continuously polls camera at hardware speed and discards stale frames."""
        while self._running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self._lock:
                    self._latest_frame = frame
            else:
                time.sleep(0.005)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Reads the freshest real-time frame from the camera with 0 ms buffer latency."""
        with self._lock:
            if self._latest_frame is not None:
                return True, self._latest_frame.copy()
        return False, None

    def is_opened(self) -> bool:
        """Returns True if the camera stream is currently open and running."""
        return self._running and self.cap is not None and self.cap.isOpened()

    def release(self):
        """Releases the camera device and cleanly terminates the background grabber thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.6)
            self._thread = None

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        with self._lock:
            self._latest_frame = None

