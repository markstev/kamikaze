#!/usr/bin/env python2
import cv2
BLUE =  (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

def main(imgpath):
  face_cascade = cv2.CascadeClassifier(
      'haarcascades/haarcascade_frontalface_default.xml')
  eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
  smile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_smile.xml')
  img = cv2.imread(imgpath)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  faces = face_cascade.detectMultiScale(gray, 1.3, 5)
  print faces
  for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), BLUE, 2)
    roi_gray = gray[y:y + h, x:x + w]
    roi_color = img[y:y + h, x:x + w]
    def plot_feature((x, y, w, h), color):
      cv2.rectangle(roi_color, (x, y), (x + w, y + h), color, 2)
    for eye in eye_cascade.detectMultiScale(roi_gray):
      plot_feature(eye, GREEN)
    for smile in smile_cascade.detectMultiScale(roi_gray):
      plot_feature(smile, RED)
  cv2.imshow('img', img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

if __name__ == "__main__":
  from sys import argv
  DEFAULT_IMG = '/home/sagarm/Pictures/Webcam/2017-06-17-153909.jpg'
  for img in (argv[1:] or [TEST_IMG]):
    main(img)
