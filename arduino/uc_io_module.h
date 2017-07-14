#ifndef NEBREE8_ARDUINO_UC_IO_MODULE_H_
#define NEBREE8_ARDUINO_UC_IO_MODULE_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"

namespace nebree8 {

const char* SET_IO = "SET_IO";
const int SET_IO_LENGTH = 6;

class UCIOModule : public arduinoio::UCModule {
 public:
  UCIOModule() {
    for (int i = 0; i < 256; ++i) {
      pins_ready_[i] = false;
    }
    status_on_ = false;
  }

  virtual const arduinoio::Message* Tick() {
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, SET_IO, SET_IO_LENGTH) == 0) {
      status_on_ = !status_on_;
      for (int i = SET_IO_LENGTH; i < length - 1; i += 2) {
        unsigned int pin = static_cast<unsigned int>(command[i]);
        bool on = command[i + 1] == 0x0 ? LOW : HIGH;
        if (!pins_ready_[pin]) {
          pinMode(pin, OUTPUT);
          pins_ready_[pin] = true;
        }
        digitalWrite(pin, on);
      }
    }
    return false;
  }

 private:
  bool pins_ready_[256];
  bool status_on_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_UC_IO_MODULE_H_
