"""Does continuous face detection on a raspi stream.

Instructions on pulling data from a picamera:
http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
"""

import opencv_test

from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# capture frames from the camera

def detect_picamera():
  # initialize the camera and grab a reference to the raw camera capture
  camera = PiCamera()
  camera.resolution = (640, 480)
  camera.framerate = 32
  raw_capture = PiRGBArray(camera, size=(640, 480))

  # allow the camera to warmup
  time.sleep(0.1)
  tt = opencv_test.CVTest()
  for frame in camera.capture_continuous(
      raw_capture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    tt.detect_and_show(image)

    # show the frame
    #cv2.imshow("Frame", image)
    #key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    raw_capture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
      break



if __name__ == "__main__":
  detect_picamera()
