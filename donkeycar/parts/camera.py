import os
import time
import numpy as np
from PIL import Image
import glob

import cv2


class BaseCamera:

    def run_threaded(self):
        return self.frame

class CameraProcessor():
    def __init__(self, resolution=(120, 160), framerate=20):
        self.processed_image = None
        self.on = True
        print('CameraProcessor loaded')

    def run(self,img_arr):
        # Process the image
        edges = cv2.Canny(img_arr,100,200)
        self.processed_image = edges

    def run_threaded(self):
        return self.processed_image

    def update(self):
        if not self.on:
            break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping CameraProcessor')
        time.sleep(.5)

class PiCamera(BaseCamera):
    def __init__(self, resolution=(120, 160), framerate=20):
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        resolution = (resolution[1], resolution[0])
        # initialize the camera and stream
        self.camera = PiCamera()  # PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        
        # Try to reduce exposure time as much as possible
        self.camera.exposure_mode = 'sports'
        self.camera.iso = 800
        
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="rgb",
                                                     use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True

        print('PiCamera loaded.. .warming camera')
        time.sleep(2)
        print('PiCamera operational, exposure speed is: ' + exposure_speed)

    def run(self):
        f = next(self.stream)
        frame = f.array
        self.rawCapture.truncate(0)
        return frame

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            if not self.on:
                break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping PiCamera')
        time.sleep(.5)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()
