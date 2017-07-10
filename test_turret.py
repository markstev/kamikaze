#!/usr/bin/env python
import time

import arduino

from robot import FakeRobot, Robot

robot = Robot("tty.usb")

time.sleep(2)
print "Created arduinio"
print("change blink")
#uno.Blink(13, 0.3)
print("sleep")
print("motor")

for i in range(6):
  for fn in [robot.left, robot.up, robot.right, robot.down]:
    fn(100)
  time.sleep(2)

# NOTE, may need to ground the enable pin beyond default wiring.
