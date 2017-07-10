#!/usr/bin/env python
import time

import arduino

uno = arduino.Arduino("ttyACM", baud=9600)


UNCONNECTED_1 = 8
UNCONNECTED_2 = 9
UNCONNECTED_3 = 12
ICE_STEPS = 6

class Motor(object):
  def __init__(self, uno, dir_pin, step_pin, trigger_neg, trigger_pos, home_dir, home_offset):
    self.uno = uno
    self.dir_pin = dir_pin
    self.step_pin = step_pin
    self.trigger_neg = trigger_neg
    self.trigger_pos = trigger_pos
    self.home_dir = home_dir
    self.home_offset = home_offset

  def Move(self, forward, steps):
    self.uno.Move(stepper_dir_pin=self.dir_pin,
                  stepper_pulse_pin=self.step_pin,
                  negative_trigger_pin=self.trigger_neg,
                  positive_trigger_pin=self.trigger_pos,
                  done_pin=UNCONNECTED_1,
                  forward=forward,
                  steps=steps,
                  final_wait=final_wait,
                  max_wait=max_wait,
                  temp_pin=UNCONNECTED_2,
                  temp_pin_threshold=ICE_STEPS)

  def Calibrate(self):
    self.Move(self.home_dir, 1500)
    self.Move(not self.home_dir, self.home_offset)

time.sleep(2)
print "Created arduinio"
print("change blink")
uno.Blink(13, 0.3)
print("sleep")
print("motor")
# Protoboard
#DIR_PIN = 12
#STEP_PIN = 11
#DIR_PIN = 3
#STEP_PIN = 2
horizontal_motor = Motor(uno,
                         dir_pin=3,
                         step_pin=2,
                         trigger_pos=6,
                         trigger_neg=UNCONNECTED_3,
                         home_dir=1,
                         home_offset=500)
vertical_motor = Motor(uno,
                       dir_pin=4,
                       step_pin=5,
                       trigger_pos=UNCONNECTED_3,
                       trigger_neg=7,
                       home_dir=0,
                       home_offset=200)

forward = 1
steps = 100
final_wait = 4000
max_wait = 4000
for motor in [horizontal_motor, vertical_motor]:
  motor.Calibrate()
  time.sleep(1)
for i in range(6):
  print 'steps =', steps
  adjusted_steps = steps
  if not forward:
    adjusted_steps *= 2
  for motor in [horizontal_motor, vertical_motor]:
    motor.Move(forward, 200)
  forward = not forward
  time.sleep(2)

# NOTE, may need to ground the enable pin beyond default wiring.
