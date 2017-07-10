#!/usr/bin/env python2

import imp
import threading
import time
import Queue

from robot import FakeRobot, Robot

try:
  CV2_FILENAME = '/home/sagarm/code/opencv/install-tree/lib/python2.7/dist-packages/'
  cv2 = imp.load_module('cv2', *imp.find_module('cv2', [CV2_FILENAME]))
except:
  print 'failed to load cv2 from ', CV2_FILENAME
  import cv2
import gflags

print "cv2 =", cv2.__file__

gflags.DEFINE_bool('preview', True, 'Enable preview window')
gflags.DEFINE_integer('webcam', 0, 'Capture device number to use')
gflags.DEFINE_bool('fake', True, 'Create actual robot?')
gflags.DEFINE_string('tty', 'ttyACM0', 'TTY for the Arduino')
FLAGS = gflags.FLAGS

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
TEAL = (255, 255, 0)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)

TARGET_CENTER = (320, 240)
TARGET_RANGE = (20, 20)
TARGET_POS = (TARGET_CENTER[0] - TARGET_RANGE[0] // 2,
              TARGET_CENTER[1] - TARGET_RANGE[1] // 2)
WIDTH = 640
HEIGHT = 480
FOV_IN_STEPS = int(90. / .3)

LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
CALIBRATE = 'calibrate'

MIN_FACE_SIZE = (20, 20)
DETECT_EYES = False
MAX_FACES = 1

def monkeypatch_nopreview():
  def do_nothing(*_args, **_kwargs):
    pass
  cv2.rectangle = do_nothing
  cv2.imshow = do_nothing
  cv2.waitKey = do_nothing

def target(img):
  print dir(img)

class Recognizer(object):
  def __init__(self, robot):
    self.face_cascade = cv2.CascadeClassifier(
        'haarcascades/haarcascade_frontalface_default.xml')
    self.eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
    self.smile_cascade = cv2.CascadeClassifier(
        'haarcascades/haarcascade_smile.xml')
    self.robot = robot
    self.last_action_time = time.time()

  @staticmethod
  def plot_feature(img, (x, y, w, h), color):
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

  @staticmethod
  def subset_array(array, (x, y, w, h)):
    return array[y:y + h, x:x + w]

  @staticmethod
  def choose_face(faces):
    if len(faces) == 0:
      return None
    def dist((x, y , w, h)):
      center = x + w//2, y + h//2
      dist = (center[0] - TARGET_CENTER[0])**2 + (center[1] - TARGET_CENTER[1])**2
      return dist
    return sorted(faces, key=dist)[0]

  def detect_and_show(self, img):
    start_time = time.clock()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    self.plot_feature(img, TARGET_POS + TARGET_RANGE, TEAL)
    faces = self.face_cascade.detectMultiScale(
        gray, 1.3, 5, minSize=MIN_FACE_SIZE)
    for face in faces:
      self.plot_feature(img, face, BLUE)
    face = self.choose_face(faces)
    actions = []
    if face is not None:
      self.plot_feature(img, self.guess_mouth_location(face), YELLOW)
      x, y, w, h = face
      for eye in (
          self.eye_cascade.detectMultiScale(self.subset_array(gray, face))
          if DETECT_EYES else []):
        self.plot_feature(self.subset_array(img, face), eye, GREEN)
      smile_roi = (x, y + 2*h//3, w, h//3)
      smile = self.smile_filter(self.smile_cascade.detectMultiScale(
          self.subset_array(gray, smile_roi)))
      if smile is not None:
        self.plot_feature(self.subset_array(img, smile_roi), smile, RED)
        smile = (smile[0] + smile_roi[0], smile[1] + smile_roi[1], smile[2],
                 smile[3])
      else:
        smile = self.guess_mouth_location(face)
      actions[:] = self.determine_action(self.mouth_center(smile))
      cv2.putText(img, ' '.join('%s(%d)' % a for a in actions),
                  (0, 40), cv2.FONT_HERSHEY_PLAIN, 2, WHITE)
    cv2.putText(img, '%.2f fps' % (1 / (time.clock() - start_time)),
                (0, 20), cv2.FONT_HERSHEY_PLAIN, 1, WHITE)
    cv2.imshow('img', img)
    for action in actions:
      self.do_action(*action)
    if time.time() - self.last_action_time > 30:
      self.do_action(CALIBRATE, 0)

  @staticmethod
  def determine_action(mouth_center):
    def to_steps(pixels):
      steps = pixels * FOV_IN_STEPS // WIDTH / 2
      print "before clamp p=%s steps=%s" % (pixels, steps)
      return min(max(steps, 4), 32)
    action = ()
    if mouth_center[0] < TARGET_POS[0]:
      action += ((LEFT, to_steps(TARGET_POS[0] - mouth_center[0])),)
    elif mouth_center[0] > TARGET_POS[0] + TARGET_RANGE[0]:
      action += ((RIGHT,
                  to_steps(mouth_center[0] - TARGET_POS[0] - TARGET_RANGE[0])),)
    if mouth_center[1] < TARGET_POS[1]:
      action += ((UP, 4),)
    elif mouth_center[1] > TARGET_POS[1] + TARGET_RANGE[1]:
      action += ((DOWN, 4),)
    return action

  @staticmethod
  def smile_filter(smiles):
    if len(smiles) == 0:
      return None
    return sorted(smiles, key=lambda s: s[2]*s[3])[-1]

  @staticmethod
  def guess_mouth_location((x, y, w, h)):
    return (x + w//4, y + 9 * h//12, w//2, h//6)

  @staticmethod
  def mouth_center(mouth):
    return mouth[0] + mouth[2]//2, mouth[1] + mouth[3]//2

  def do_action(self, dir, steps):
    """action is one of the LEFT, RIGHT, UP, DOWN constants."""
    if dir is LEFT:
      self.robot.left(steps)
    elif dir is RIGHT:
      self.robot.right(steps)
    elif dir is UP:
      self.robot.up(steps)
    elif dir is DOWN:
      self.robot.down(steps)
    elif dir is CALIBRATE:
      self.robot.calibrate()
    self.last_action_time = time.time()

def detect_webcam(recognizer):
  q = Queue.Queue(maxsize=1000)
  done = [False]
  def read_images():
    try:
      cap = cv2.VideoCapture(FLAGS.webcam)
      if not cap.isOpened():
        raise RuntimeError("Failed to open camera")
      while not done[0]:
        _, frame = cap.read()
        try:
          q.put_nowait(frame)
        except Queue.Full:
          pass
    finally:
      cap.release()
  def process_images():
    while True:
      latest = q.get()
      while True:
        try:
          latest = q.get_nowait()
        except Queue.Empty:
          break
      try:
        recognizer.detect_and_show(latest)
      except cv2.error:
        # Sometimes, cvtcolor fails.
        continue
      key = cv2.waitKey(delay=1000//30)
      if key == ord('p'):
        key = cv2.waitKey(0)
      if key == ord('q'):
        break
    done[0] = True
  read_thread = threading.Thread(target=read_images)
  read_thread.start()
  while True:
    process_images()
  #process_thread = threading.Thread(target=process_images)
  #process_thread.start()
  read_thread.join()
  #process_thread.join()

def detect_images(paths, recognizer):
  for img in paths:
    print '==', img
    recognizer.detect_and_show(cv2.imread(img))
    key = cv2.waitKey(0)
    if key == ord('q'):
      break

def main():
  from sys import argv
  argv = FLAGS(argv)
  recognizer = Recognizer(FakeRobot() if FLAGS.fake else Robot(FLAGS.tty))
  if not FLAGS.preview:
    monkeypatch_nopreview()
  try:
    if len(argv) == 1:
      detect_webcam(recognizer)
    else:
      detect_images(argv[1:], recognizer)
  finally:
    cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
