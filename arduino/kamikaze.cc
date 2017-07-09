#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif 
#include <SoftwareSerial.h>
#include <Wire.h>  // Needed by cmake to generate the pressure sensor deps. (Gross!)

#include "../arduinoio/lib/serial_module.h"
#include "../arduinoio/lib/arduinoio.h"
#include "blink_module.h"
#include "motor_module.h"

const int SERIAL_RX_PIN = 0;
const int SERIAL_TX_PIN = 1;
const int LED_SIGNAL_PIN = 51;


//SoftwareSerial *serial;

//HX711 scale(DAT_PIN, CLK_PIN);
//float calibration_factor = -7050; //-7050 worked for my 440lb max scale setup

arduinoio::ArduinoIO arduino_io;
void setup() {
  Serial.begin(9600);
//Serial.println("HX711 calibration sketch");
//  Serial.println("Remove all weight from scale");
//    Serial.println("After readings begin, place known weight on scale");
//      Serial.println("Press + or a to increase calibration factor");
//        Serial.println("Press - or z to decrease calibration factor");

//          scale.set_scale();
//            scale.tare(); //Reset the scale to 0

//              long zero_factor = scale.read_average(); //Get a baseline reading
//                Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
//                  Serial.println(zero_factor);
  arduino_io.Add(new arduinoio::SerialRXModule(NULL, 0));
  arduino_io.Add(new nebree8::BlinkModule());
  arduino_io.Add(new nebree8::MotorModule());
}

int mode = HIGH;

void loop() {
//digitalWrite(11, mode);
//mode = !mode;
//delayMicroseconds(1000);

  arduino_io.HandleLoopMessages();
  
//scale.set_scale(calibration_factor); //Adjust to this calibration factor

//Serial.print("Reading: ");
//Serial.print(scale.get_units(), 1);
//Serial.print(" lbs"); //Change this to kg and re-adjust the calibration factor if you follow SI units like a sane person
//Serial.print(" calibration_factor: ");
//Serial.print(calibration_factor);
//Serial.println();

//if(Serial.available())
//{
//  char temp = Serial.read();
//  if(temp == '+' || temp == 'a')
//    calibration_factor += 10;
//  else if(temp == '-' || temp == 'z')
//    calibration_factor -= 10;
//}

}
