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

# UNCONNECTED
UC_TRIGGER_POS = 12  # Should not be in use
UC_STEPPER_DONE = 8  # Unused
UC_ICE_PIN = 7  # Unused
UC_ICE_STEPS = 6  # Unused

class FakeRobot(object):
  def left(self, *args): pass
  def right(self, *args): pass
  def up(self, *args): pass
  def down(self, *args): pass

class Robot(object):
  def __init__(self, port="ttyACM0"):
    self.uno = arduino.Arduino(port, baud=9600)
    time.sleep(2)
    self.uno.Blink(13, 0.3)

  def left(self, steps):
    return self.__left_right(False, steps)

  def right(self, steps):
    return self.__left_right(True, steps)

  def __left_right(self, right, steps):
    return self.move(
        dir_pin=LR_DIR_PIN,
        pulse_pin=LR_PULSE_PIN,
        trigger_pin=LR_TRIGGER_NEG,
        forward=right,
        steps=steps)

  def up(self, steps): #pylint: disable=invalid-name
    return self.__up_down(True, steps)

  def down(self, steps):
    return self.__up_down(False, steps)

  def __up_down(self, up, steps): #pylint: disable=invalid-name
    return
    return self.move(
        dir_pin=UD_DIR_PIN,
        pulse_pin=UD_PULSE_PIN,
        trigger_pin=UD_TRIGGER_NEG,
        forward=up,
        steps=steps)

  def move(self, dir_pin, pulse_pin, trigger_pin, forward, steps):
    self.uno.Move(stepper_dir_pin=dir_pin,
                  stepper_pulse_pin=pulse_pin,
                  negative_trigger_pin=trigger_pin,
                  positive_trigger_pin=UC_TRIGGER_POS,
                  done_pin=UC_STEPPER_DONE,
                  forward=forward,
                  steps=steps,
                  final_wait=FINAL_WAIT,
                  max_wait=MAX_WAIT,  # MIN_WAIT on Arduino is currently 10k.
                  temp_pin=0,
                  temp_pin_threshold=0)


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
