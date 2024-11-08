import cv2
import time
import threading
import queue
import cv2, queue, threading, time

# bufferless VideoCapture
class VideoCapture:
    def __init__(self, name, skip_fps=0, queue_size=150):
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue(maxsize=queue_size)
        self.lock = threading.Lock()
        self.running = True  # Flag to indicate if the thread should keep running
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.skip_fps = skip_fps
        self.frame_count = 0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) 
        self.frame_interval = int(self.cap.get(cv2.CAP_PROP_FPS) / self.skip_fps)
        self.t.start()

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # Discard previous frame
                except queue.Empty:
                    pass
            
            while self.q.full():
                time.sleep(0.01)
                if not self.running:
                    return
                
            # Save the frame if it is at the specified interval
            if self.frame_count % self.frame_interval == 0:
                self.q.put(cv2.resize(frame, (640, 360)))

            self.frame_count += 1
            self.state=ret

    def read(self):
        return self.q.get(),self.state

    def stop(self):
        self.running = False
        self.t.join()  # Wait for the thread to exit