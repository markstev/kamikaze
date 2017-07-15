#!/usr/bin/env python
import time

import arduino
# Protoboard
#DIR_PIN = 12
#STEP_PIN = 11
#DIR_PIN = 3
#STEP_PIN = 2
LR_DIR_PIN = 4
LR_PULSE_PIN = 5
LR_TRIGGER_NEG = 6

UD_DIR_PIN = 0
UD_PULSE_PIN = 1
UD_TRIGGER_NEG = 7

FINAL_WAIT = 4000
MAX_WAIT = 4000

UNCONNECTED_1 = 17
UNCONNECTED_2 = 18
UNCONNECTED_3 = 12
UC_ICE_STEPS = 6  # Unused

UP_DOWN_MS1 = 8
UP_DOWN_MS2 = 9
UP_DOWN_MS3 = 10
LEFT_RIGHT_MS1 = 14
LEFT_RIGHT_MS2 = 15
LEFT_RIGHT_MS3 = 16

UP_DIR = 0
LEFT_DIR = 1

FINAL_WAIT = 4000
MAX_WAIT = 4000

FULL = "FULL"
HALF = "HALF"
QUARTER = "QUARTER"
EIGHTH = "EIGHTH"
SIXTEENTH = "SIXTEENTH"

class Motor(object):
  def __init__(self, uno, dir_pin, step_pin, trigger_neg, trigger_pos, home_dir, home_offset, ms1, ms2, ms3):
    self.uno = uno
    self.dir_pin = dir_pin
    self.step_pin = step_pin
    self.trigger_neg = trigger_neg
    self.trigger_pos = trigger_pos
    self.home_dir = home_dir
    self.home_offset = home_offset
    self.ms1 = ms1
    self.ms2 = ms2
    self.ms3 = ms3

  def Move(self, forward, steps):
    COARSENESS = 256
    if steps < COARSENESS:
      self.SetSpeed(SIXTEENTH)
    elif steps < COARSENESS * 2:
      self.SetSpeed(EIGHTH)
      steps /= 2
    elif steps < COARSENESS * 4:
      self.SetSpeed(QUARTER)
      steps /= 4
    elif steps < COARSENESS * 8:
      self.SetSpeed(HALF)
      steps /= 8
    else:
      self.SetSpeed(FULL)
      steps /= 16
    self.uno.Move(stepper_dir_pin=self.dir_pin,
                  stepper_pulse_pin=self.step_pin,
                  negative_trigger_pin=self.trigger_neg,
                  positive_trigger_pin=self.trigger_pos,
                  done_pin=UNCONNECTED_1,
                  forward=forward,
                  steps=steps,
                  final_wait=FINAL_WAIT,
                  max_wait=MAX_WAIT,
                  temp_pin=UNCONNECTED_2,
                  temp_pin_threshold=UC_ICE_STEPS)

  def Calibrate(self):
    self.Move(self.home_dir, 1500)
    self.Move(not self.home_dir, self.home_offset)

  def SetSpeed(self, speed):
    print "Speed = %s" % speed
    self.speed = speed
    if speed == FULL:
      self.uno.WriteOutput(self.ms1, 0)
      self.uno.WriteOutput(self.ms2, 0)
      self.uno.WriteOutput(self.ms3, 0, True)
    elif speed == HALF:
      self.uno.WriteOutput(self.ms1, 1)
      self.uno.WriteOutput(self.ms2, 0)
      self.uno.WriteOutput(self.ms3, 0, True)
    elif speed == QUARTER:
      self.uno.WriteOutput(self.ms1, 0)
      self.uno.WriteOutput(self.ms2, 1)
      self.uno.WriteOutput(self.ms3, 0, True)
    elif speed == EIGHTH:
      self.uno.WriteOutput(self.ms1, 1)
      self.uno.WriteOutput(self.ms2, 1)
      self.uno.WriteOutput(self.ms3, 0, True)
    elif speed == SIXTEENTH:
      self.uno.WriteOutput(self.ms1, 1)
      self.uno.WriteOutput(self.ms2, 1)
      self.uno.WriteOutput(self.ms3, 1, True)

class FakeRobot(object):
  def left(self, *args): pass
  def right(self, *args): pass
  def up(self, *args): pass
  def down(self, *args): pass
  def calibrate(self): pass

class Robot(object):
  def __init__(self, port="ttyACM0"):
    self.uno = arduino.Arduino(port, baud=9600)
    time.sleep(2)
    self.uno.Blink(13, 0.3)

    self.horizontal_motor = Motor(
        self.uno,
        dir_pin=3,
        step_pin=2,
        trigger_pos=6,
        trigger_neg=UNCONNECTED_3,
        home_dir=1,
        home_offset=500,
        ms1=LEFT_RIGHT_MS1,
        ms2=LEFT_RIGHT_MS2,
        ms3=LEFT_RIGHT_MS3)
    self.vertical_motor = Motor(
        self.uno,
        dir_pin=4,
        step_pin=5,
        trigger_pos=UNCONNECTED_3,
        trigger_neg=7,
        home_dir=0,
        home_offset=200,
        ms1=UP_DOWN_MS1,
        ms2=UP_DOWN_MS2,
        ms3=UP_DOWN_MS3)
    self.calibrate()

  def calibrate(self):
    for motor in [self.horizontal_motor, self.vertical_motor]:
      motor.Calibrate()

  def left(self, steps):
    self.horizontal_motor.Move(LEFT_DIR, steps)

  def right(self, steps):
    self.horizontal_motor.Move(not LEFT_DIR, steps)

  def up(self, steps): #pylint: disable=invalid-name
    self.vertical_motor.Move(UP_DIR, steps)

  def down(self, steps):
    self.vertical_motor.Move(not UP_DIR, steps)


if __name__ == "__main__":
  robot = Robot("ttyACM1")
  STEPS = 8
  while False:
    robot.left(STEPS)
    time.sleep(.5)
    robot.right(STEPS)
    time.sleep(.5)
  while True:
    robot.up(STEPS)
    time.sleep(.5)
    robot.down(STEPS)
    time.sleep(.5)
