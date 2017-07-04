#!/usr/bin/env python2

import sys

import cv2

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
TEAL = (255, 255, 0)
YELLOW = (0, 255, 255)
DEFAULT_IMG = '/home/sagarm/Pictures/Webcam/2017-06-17-153909.jpg'
TARGET_POS = (100, 100)
TARGET_RANGE = (5,5)

DETECT_EYES = False
MAX_FACES = 1

def monkeypatch_nopreview():
  def do_nothing(*args, **kwargs): pass
  cv2.rectangle = do_nothing
  cv2.imshow = do_nothing
  cv2.waitKey = do_nothing

def target(img):
  print dir(img)

class Recognizer(object):
  def __init__(self):
    self.face_cascade = cv2.CascadeClassifier(
        'haarcascades/haarcascade_frontalface_default.xml')
    self.eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
    self.smile_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_smile.xml')

  def plot_feature(self, img, (x, y, w, h), color):
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

  def detect_and_show(self, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    self.plot_feature(img, TARGET_POS + TARGET_RANGE, TEAL)
    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
    for face in faces[:MAX_FACES]:
      self.plot_feature(img, face, BLUE)
      self.plot_feature(img, self.guess_mouth_location(face), YELLOW)
      x, y, w, h = face
      roi_gray = gray[y:y + h, x:x + w]
      roi_color = img[y:y + h, x:x + w]
      for eye in (
          self.eye_cascade.detectMultiScale(roi_gray) if DETECT_EYES else []):
        self.plot_feature(roi_color, eye, GREEN)
      smile_roi_gray = gray[y + 2*h//3:y + h, x:x + w]
      smile_roi_color = img[y + 2*h//3:y + h, x:x + w]
      smile = self.smile_filter(
          self.smile_cascade.detectMultiScale(smile_roi_gray))
      if smile is not None:
        self.plot_feature(smile_roi_color, smile, RED)
    cv2.imshow('img', img)

  def smile_filter(self, smiles):
    if len(smiles) == 0: return None
    return sorted(smiles, key=lambda s: s[2]*s[3])[-1]

  def guess_mouth_location(self, (x, y, w, h)):
    return (x + w//4, y + 4 * h//6, w//2, h//6)

def detect_webcam():
  tt = Recognizer()
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
  tt = Recognizer()
  for img in paths or [DEFAULT_IMG]:
    print '==', img
    tt.detect_and_show(cv2.imread(img))
    key = cv2.waitKey(0)
    if key == ord('q'):
      break

if __name__ == "__main__":
  monkeypatch_nopreview()
  try:
    if len(sys.argv) == 1:
      detect_webcam()
    else:
      detect_images(sys.argv[1:])
  finally:
    cv2.destroyAllWindows()
