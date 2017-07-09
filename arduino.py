import logging
import struct
import threading
import time
import Queue

from arduinoio import serial_control

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S')

_REFRESH_RATE = 5  # Refreshes per second


class Arduino:
  def __init__(self, device_basename="ttyACM", baud=115200):
    self.interface = serial_control.SerialInterface(device_basename, baud=baud)
    self.outputs = {}
    self.signal_refresh = Queue.Queue(1)
    self.done_ack = Queue.Queue(1)
    self.incoming_messages = Queue.Queue(10)
    self.output_updates = Queue.Queue(100)
    self.thread = threading.Thread(target=self.__RefreshOutputs)
    self.thread.daemon = True
    self.thread.start()

  def WriteOutput(self, pin, value, blocking=False):
    try:
      self.output_updates.put((pin, value), block=True)
      for i in range(1):
        # Ensures that the data is really written (if blocking)
        self.signal_refresh.put((False, None), block=blocking, timeout=None)
    except Queue.Full:
      print "Error, aurdino signal_refresh queue full."
      pass

  def WriteServo(self, pin, start_degrees, end_degrees, seconds):
    raw_message = [chr(pin), chr(start_degrees), chr(end_degrees), chr(seconds)]
    command = "SERVO" + "".join(raw_message)
    self.interface.Write(0, command)
    print "set servo"

  def Blink(self, pin, seconds):
    centi_secs = int(round(seconds * 10))
    raw_message = [chr(pin), chr(centi_secs)]
    command = "BLINK" + "".join(raw_message)
    self.interface.Write(0, command)

  def WriteDelay(self, pin, on, seconds):
    pin = pin.value - 2000
    self.WriteDelayRaw(pin, on, seconds)

  def WriteDelayRaw(self, pin, on, seconds):
    centi_secs = int(round(seconds * 10))
    print pin
    print on
    print centi_secs
    raw_message = [chr(pin), chr(on), chr(centi_secs)]
    command = "DELAY" + "".join(raw_message)
    self.interface.Write(0, command)

  def HoldPressure(self, pressure_valve_pin, hold=True):
    min_pressure_psi = 15.8
    max_pressure_psi = 16.1
    min_pressure_mbar = min_pressure_psi * 1014 / 14.7
    max_pressure_mbar = max_pressure_psi * 1014 / 14.7
    raw_message = []
    raw_message.extend(struct.unpack('4B', struct.pack('<f',
                                                       min_pressure_mbar)))
    raw_message.extend(struct.unpack('4B', struct.pack('<f',
                                                       max_pressure_mbar)))
    raw_message = [chr(x) for x in raw_message]
    raw_message.extend((chr(hold), chr(pressure_valve_pin)))
    command = "HOLDP" + "".join(raw_message)
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def SetLed(self, x, y, red, green, blue):
    raw_message = [red, green, blue]
    raw_message.extend(struct.unpack('4B', struct.pack('<f', x)))
    raw_message.extend(struct.unpack('4B', struct.pack('<f', y)))
    raw_message = [chr(x) for x in raw_message]
    command = "ONE_LED" + "".join(raw_message)
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def AllLed(self, red, green, blue):
    raw_message = [red, green, blue]
    raw_message = [chr(x) for x in raw_message]
    command = "ALL_LED" + "".join(raw_message)
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def UpdateLeds(self):
    command = "LED_GO"
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def Servo(self, servo_pin, servo_degrees):
    raw_message = []
    raw_message.extend((servo_pin, servo_degrees))
    raw_message = [chr(x) for x in raw_message]
    command = "SERV" + "".join(raw_message)
    print "Servo command: %s" % [ord(x) for x in raw_message]
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def Move(self, stepper_dir_pin, stepper_pulse_pin, negative_trigger_pin,
           positive_trigger_pin, done_pin, forward, steps, final_wait,
           max_wait, temp_pin, temp_pin_threshold):
    raw_message = []
    if forward:
      forward = 0x01
    else:
      forward = 0x00
    raw_message.extend((stepper_dir_pin, stepper_pulse_pin,
                        negative_trigger_pin, positive_trigger_pin, done_pin,
                        forward))
    if max_wait < 1000:
      raw_message.append(10)
    else:
      raw_message.append(0)
    raw_message.append(temp_pin)
    raw_message.extend(struct.unpack('4B', struct.pack('<i', steps)))
    raw_message.extend(struct.unpack('4B', struct.pack('<i', temp_pin_threshold)))
    # print "max_wait: %s" % max_wait
    # raw_message.extend(struct.unpack('4B', struct.pack('<i', 4000)))
    raw_message = [chr(x) for x in raw_message]
    command = "MOVE" + "".join(raw_message)
    print "Move command: %s" % [ord(x) for x in raw_message]
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def __SendOutputsMessage(self):
    raw_message = []
    for pin, value in self.outputs.iteritems():
      raw_message.append(chr(pin))
      raw_message.append(chr(value))
    batch_size = 40  # MUST BE EVEN
    for batch in range(0, len(raw_message) / batch_size + 1):
      start = batch * batch_size
      end = start + batch_size
      command = "SET_IO" + "".join(raw_message[start:end])
      self.interface.Write(0, command)

  def __RefreshOutputs(self):
    while True:
      try:
        use_this_command, command = self.signal_refresh.get(True,
                                                            1. / _REFRESH_RATE)
        while True:
          try:
            pin, value = self.output_updates.get(False)
            self.outputs[pin] = value
          except Queue.Empty:
            break
        if use_this_command:
          self.interface.Write(0, command)
        else:
          self.__SendOutputsMessage()
      except Queue.Empty:
        # No refresh signals for a while, Refresh all pins
        self.__SendOutputsMessage()
      message = None  #self.interface.Read(no_checksums=True)
      if message:
        try:
          self.incoming_messages.put((False, None), block=False, timeout=None)
        except Queue.Full:
          pass


def main():
  arduino = Arduino()
  while True:
    arduino.WriteOutput(2, 1)
    time.sleep(1.0)
    for pin in [6, 13, 12, 11, 10, 9, 2]:
      for setting in [0, 1]:
        arduino.WriteOutput(pin, setting)
        time.sleep(1.0)
    time.sleep(5)
    print "should be done"

  # end = 160
  # middle = 100
  # ts = 3
  # arduino.WriteServo(22, end, middle, ts)
  # arduino.WriteServo(21, 180, 90, ts)
  # time.sleep(10)
  # print "should be done"
  # time.sleep(2)
  # arduino.WriteServo(22, 90, 180, ts)
  # arduino.WriteServo(21, 90, 180, ts)
  # time.sleep(10)
  # print "should be done"


if __name__ == "__main__":
  main()
