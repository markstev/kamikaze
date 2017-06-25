#!/usr/bin/env python2

import sys

import cv2

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
DEFAULT_IMG = '/home/sagarm/Pictures/Webcam/2017-06-17-153909.jpg'

class CVTest(object):
  def __init__(self):
    self.face_cascade = cv2.CascadeClassifier(
        'haarcascades/haarcascade_frontalface_default.xml')
    self.eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
    self.smile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_smile.xml')

  def detect_and_show(self, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
      print "face =", (x, y, w, h)
      cv2.rectangle(img, (x, y), (x + w, y + h), BLUE, 2)
      roi_gray = gray[y:y + h, x:x + w]
      roi_color = img[y:y + h, x:x + w]
      def plot_feature((x, y, w, h), color):
        cv2.rectangle(roi_color, (x, y), (x + w, y + h), color, 2)
      for eye in self.eye_cascade.detectMultiScale(roi_gray):
        print "eye =", eye
        plot_feature(eye, GREEN)
      for smile in self.smile_cascade.detectMultiScale(roi_gray):
        print "smile = ", smile
        plot_feature(smile, RED)
    cv2.imshow('img', img)

def detect_webcam():
  tt = CVTest()
  try:
    cap = cv2.VideoCapture(0)
    while True:
      _, frame = cap.read()
      tt.detect_and_show(frame)
      key = cv2.waitKey(delay=1000//30)
      if key == ord('p'): 
        key = cv2.waitKey(0)
      if key == ord('q'):
        break
  finally:
    cap.release()

def detect_images(paths):
  tt = CVTest()
  for img in paths or [DEFAULT_IMG]:
    tt.detect_and_show(cv2.imread(img))
    key = cv2.waitKey(0)
    if key == ord('q'): break

if __name__ == "__main__":
  try:
    if len(sys.argv) == 1:
      detect_webcam()
    else:
      detect_images(sys.argv[1:])
  finally:
    cv2.destroyAllWindows()
