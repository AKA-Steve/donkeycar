import os
import time
import numpy as np
from PIL import Image
import glob

import cv2


# https://towardsdatascience.com/image-pre-processing-c1aec0be3edf

class BaseCamera:

    def run_threaded(self):
        if self.last_frame == self.frame:
            print("Warning: returning same image")
        self.last_frame = self.frame
        return self.frame

class CameraProcessor():
    def __init__(self, resolution=(120, 160), framerate=20):
        self.processed_image = None
        self.on = True
        print('CameraProcessor loaded')

    def run(self,img_arr = None):
        # Process the image
        #self.processed_image = cv2.Canny(img_arr,100,200)
        blur = cv2.GaussianBlur(img_arr,(5,5),0)
        #gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        ret, self.processed_image = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return self.processed_image

    def update(self):
        return

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping CameraProcessor')
        time.sleep(.5)
        
class TestCam(BaseCamera):
    def __init__(self, resolution=(120, 160), framerate=20):
        self.frame = cv2.imread('Neptune_Full.jpg',0)
        
    def run(self):
        return self.frame

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
