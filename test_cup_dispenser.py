#!/usr/bin/env python
import time

import arduino

uno = arduino.Arduino("ttyACM1", baud=9600)

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
DIR_PIN = 4
STEP_PIN = 5
# UNCONNECTED
TRIGGER_NEG = 6
TRIGGER_POS = 2  # Should not be in use
STEPPER_DONE = 8
ICE_PIN = 7
ICE_STEPS = 6

forward = 1
steps = 200
final_wait = 4000
max_wait = 4000
for i in range(50):
  print 'steps =', steps
  for i in range(10):
    uno.Move(stepper_dir_pin=DIR_PIN,
             stepper_pulse_pin=STEP_PIN,
             negative_trigger_pin=TRIGGER_NEG,
             positive_trigger_pin=TRIGGER_POS,
             done_pin=STEPPER_DONE,
             forward=forward,
             steps=steps // 10,
             final_wait=final_wait,
             max_wait=max_wait,
             temp_pin=ICE_PIN,
             temp_pin_threshold=ICE_STEPS)
    time.sleep(.1)
  forward = not forward
  """
  if not forward:
    steps *= 2
  else:
    steps /= 2
  """
  time.sleep(2)

# NOTE, may need to ground the enable pin beyond default wiring.
