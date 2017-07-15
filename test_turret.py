#!/usr/bin/env python
import time

import arduino

from robot import FakeRobot, Robot

robot = Robot("ttyACM1")

time.sleep(2)
print "Created arduinio"
print("change blink")
#uno.Blink(13, 0.3)
print("sleep")
print("motor")

for i in range(60):
  #for fn in [robot.left, robot.up, robot.right, robot.down]:
  for fn in [robot.up, robot.down]:
    fn(20 + (i % 5) * 400)
  time.sleep(2)

# NOTE, may need to ground the enable pin beyond default wiring.
