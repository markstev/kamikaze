#ifndef NEBREE8_ARDUINO_MOTOR_MODULE_H_
#define NEBREE8_ARDUINO_MOTOR_MODULE_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"

namespace nebree8 {

const char* MOVE = "MOVE";
const int MOVE_LENGTH = 4;
const double SPEED_UP_FACTOR = 0.996;
const double SLOW_DOWN_FACTOR = 1.004;
const int SLOW_DOWN_INCREMENT = 100;
const double SLOW_DOWN_FACTOR_INCREMENT = 1.49063488565;

class MotorModule : public arduinoio::UCModule {
 public:
  MotorModule() {
    pulse_state_ = false;
    initialized_ = false;
    timed_callback_ = NULL;
    max_wait_ = 8000;
    send_done_ = false;

    const int kLocalAddress = 0;
    const int kDoneSize = 5;
    char command[kDoneSize];
    strncpy(command, "MDONE", kDoneSize);
    done_message_.Reset(kLocalAddress, kDoneSize, (unsigned char*) command);
  }

  virtual const arduinoio::Message* Tick() {
    if (timed_callback_ != NULL) {
      timed_callback_->Update();
    }
    if (send_done_) {
      send_done_ = false;
      return &done_message_;
    }
    return NULL;
  }

  void StepMotor() {
    --remaining_steps_;
    pulse_state_ = !pulse_state_;
    digitalWrite(pulse_pin_, pulse_state_ ? HIGH : LOW);
    if (TimeToSlowDown(remaining_steps_)) {
      current_wait_ *= SLOW_DOWN_FACTOR;
    } else if (current_wait_ > min_wait_) {
      current_wait_ *= SPEED_UP_FACTOR;
    }
    if (temp_pin_ > 0) {
      if (remaining_steps_ > temp_pin_steps_) {
        digitalWrite(temp_pin_, HIGH);
      } else {
        digitalWrite(temp_pin_, LOW);
      }
    }
    if (remaining_steps_ > 0) {
      char relevant_trigger_pin =
          moving_positive_ ? trigger_positive_pin_ : trigger_negative_pin_;
      // on a pull-up -> not triggered
      if (digitalRead(relevant_trigger_pin) == HIGH) {
        timed_callback_ = new arduinoio::TimedCallback<MotorModule>(
            true, current_wait_, this, &MotorModule::StepMotor);
        return;
      }
    }
    digitalWrite(done_pin_, HIGH);
    send_done_ = true;
    timed_callback_ = NULL;
  }

  bool TimeToSlowDown(int steps_remaining) {
    const int steps_increment = steps_remaining / SLOW_DOWN_INCREMENT;
    double new_wait = current_wait_;
    for (int i = 0; i < steps_increment; ++i) {
      new_wait *= SLOW_DOWN_FACTOR_INCREMENT;
      if (new_wait > max_wait_) {
        // We can wait and still slow down in time.
        return false;
      }
    }
    return true;
  }

  template <typename T>
  bool Update(const T &new_value, T* old_value) {
    const bool changed = new_value != *old_value;
    *old_value = new_value;
    return changed;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (length > MOVE_LENGTH &&
        (strncmp(command, MOVE, MOVE_LENGTH) == 0)) {
      // dir pin (char)
      // pulse pin (char)
      // trigger negative pin (char)
      // trigger positive pin (char)
      // forward? (char)
      // steps (int32)
      // max_frequency (int32) = 1 / min_wait_
      char dir_pin = command[MOVE_LENGTH];
      bool changed = Update(command[MOVE_LENGTH + 1], &pulse_pin_);
      changed |= Update(command[MOVE_LENGTH + 2], &trigger_negative_pin_);
      changed |= Update(command[MOVE_LENGTH + 3], &trigger_positive_pin_);
      changed |= Update(command[MOVE_LENGTH + 4], &done_pin_);
      if (changed) {
        initialized_ = false;
      }
      moving_positive_ = command[MOVE_LENGTH + 5] != 0x00;
      if (command[MOVE_LENGTH + 6] > 5) {
        max_wait_ = 8000;
      } else {
        max_wait_ = 8000;
      }
      send_done_ = false;
      temp_pin_ = command[MOVE_LENGTH + 7];
      
      const int *int_args = (const int*) (command + MOVE_LENGTH + 8);
      remaining_steps_ = int_args[0];
      const int *temp_int_args = (const int*) (command + MOVE_LENGTH + 12);
      temp_pin_steps_ = temp_int_args[0];
      min_wait_ = 4000;
      if (!initialized_) {
        // Assumes the pins won't change.
        pinMode(dir_pin, OUTPUT);
        pinMode(pulse_pin_, OUTPUT);
        pinMode(done_pin_, OUTPUT);
        pinMode(trigger_negative_pin_, INPUT_PULLUP);
        pinMode(trigger_positive_pin_, INPUT_PULLUP);
        initialized_ = true;
      }
      digitalWrite(done_pin_, LOW);
      digitalWrite(dir_pin, moving_positive_ ? HIGH : LOW);
      current_wait_ = max_wait_;
      timed_callback_ = new arduinoio::TimedCallback<MotorModule>(true, current_wait_,
          this,
          &MotorModule::StepMotor);
      while (!send_done_) {
        timed_callback_->Update();
      }
      send_done_ = false;
    }
    return true;
  }

 private:
  bool pulse_state_;

  bool initialized_;
  char pulse_pin_;
  char trigger_negative_pin_;
  char trigger_positive_pin_;
  char done_pin_;

  bool moving_positive_;
  float min_wait_;
  int max_wait_;
  float current_wait_;
  int remaining_steps_;
  char temp_pin_;
  int temp_pin_steps_;

  bool send_done_;
  arduinoio::Message done_message_;

  arduinoio::TimedCallback<MotorModule> *timed_callback_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_MOTOR_MODULE_H_
