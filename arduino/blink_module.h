#ifndef NEBREE8_NANO_BLINK_MODULE_H_
#define NEBREE8_NANO_BLINK_MODULE_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"

namespace nebree8 {

const char* BLINK = "BLINK";
const int BLINK_LENGTH = 5;

class BlinkModule : public arduinoio::UCModule {
 public:
  BlinkModule() {
    on_ = 0x00;
    pin_ = 13;
    pinMode(pin_, OUTPUT);
    pinMode(12, OUTPUT);
    pinMode(11, OUTPUT);
    // msec
    delay_ = 1000;
    Blink();
  }

  virtual const arduinoio::Message* Tick() {
    if (timed_callback_ != NULL) {
      timed_callback_->Update();
    }
    return NULL;
  }

  void Blink() {
    digitalWrite(pin_, on_);
    on_ = on_ == 0x00 ? 0x01 : 0x00;
    timed_callback_ = new arduinoio::TimedCallback<BlinkModule>(
        delay_,
        this,
        &BlinkModule::Blink);
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, BLINK, BLINK_LENGTH) == 0) {
      pin_ = command[BLINK_LENGTH];
      pinMode(pin_, OUTPUT);
      delay_ = static_cast<unsigned long>(command[BLINK_LENGTH + 1]) * 100;
      delete timed_callback_;
      Blink();
      return true;
    }
    return false;
  }

 private:
  char on_;
  char pin_;
  unsigned long delay_;
  arduinoio::TimedCallback<BlinkModule> *timed_callback_;
};

}  // namespace nebree8

#endif  // NEBREE8_NANO_BLINK_MODULE_H_
