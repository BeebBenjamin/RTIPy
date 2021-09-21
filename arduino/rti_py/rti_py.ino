/*
MIT License

Copyright (c) 2021 Richard Benjamin Allen, Palaeopi Limited

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEA

IR pulse code adapted from the work of luckylarry https://web.archive.org/web/20170702094336/http://luckylarry.co.uk/category/passing-time/photography/cameras/
The IR sequence used was originally taken from: http://www.bigmike.it/ircontrol/
*/

#include <avr/pgmspace.h>
#include <Charliplexing.h>

String incomingString;
String conditions;
String led;
int count;

String getValue(String data, char separator, int index) {
  /*
    Parses the setup string to separate out variables from a comma delimited list
    @param data String containing the commands to parse
    @param separator char containing the character to use as a delimiter
    @param index number of delimiter to start parsing from
    @return String containing a subcommand parsed out of the initial data
  */
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void pulse_on(int pulseTime) {
/*
    Turns an IR LED on and off in a pulse designed for Nikon cameras
    @param pulseTime Int of the time the IR LED is on
*/
  unsigned long endPulse = micros() + pulseTime;
  while ( micros() < endPulse) {
    digitalWrite(A0, HIGH);
    delayMicroseconds(13);
    digitalWrite(A0, LOW);
    delayMicroseconds(13);
  }
}

void pulse_off(unsigned long startDelay) {
/*
    Makes the Arduino wait for the specified time
    in micro seconds.
    @param startDelay Long integer of the time the IR LED is off
*/
  unsigned long endDelay = micros() + startDelay;
  while (micros() < endDelay);
}

void takePicture() {
/*
    The Nikon camera pulse sequence which is fired twice in
    succession in order to trigger the camera shutter.
*/
  for (int i = 0; i < 2; i++) {
    pulse_on(2000);
    pulse_off(27850);
    pulse_on(390);
    pulse_off(1580);
    pulse_on(410);
    pulse_off(3580);
    pulse_on(400);
    pulse_off(63200);
  }
}

void setup() {
/*
    Specify analogue pin A0 for the IR LED, define LedSign variable
    for use in the Charlieplexing (Lolshield) library functions, and
    begin the USB serial communication.
*/
  pinMode(A0, OUTPUT);
  Serial.begin(9600);
  LedSign::Init();
}

void loop() {
/*
    Reads commands incoming over the USB serial port and switches
    operation accordingly between three separate modes, L for Light
    which lights a single fixed LED to allow for camera setup, T for
    Tweak which lights a single addressed LED to allow for adjusting
    it's position with the blue tack, and C for Capture which initiates
    the timed camera trigger and LED lighting sequence.
*/
  uint8_t i;
  if (Serial.available() > 0) {
    incomingString = Serial.readString();
    String instructionByte = getValue(incomingString,',',0); 
    Serial.print("I received: ");
    Serial.print(incomingString);
    Serial.print(" the instructionByte was: ");
    Serial.print(instructionByte);

    if (instructionByte == "L") {
      Serial.print("I should be lighting an LED right now!");
      LedSign::Set(3, 0, 1);
      delay(60000);
      LedSign::Set(3, 0, 0);
    }
    else if (instructionByte == "T") {
      String led_x = getValue(incomingString, ',', 1);
      String led_y = getValue(incomingString, ',', 2);
      String led_delay = getValue(incomingString, ',', 3);

      LedSign::Set(led_x.toInt(), led_y.toInt(), 1);

      delay(led_delay.toInt()*1000);

      LedSign::Set(led_x.toInt(), led_y.toInt(), 0);
    }
    else if (instructionByte == "C") {
      String delay_before = getValue(incomingString, ',', 1);
      String delay_after = getValue(incomingString, ',', 2);
      String intLowerOne = getValue(incomingString, ',', 3);
      String intUpperOne = getValue(incomingString, ',', 4);
      String intLowerTwo = getValue(incomingString, ',', 5);
      String intUpperTwo = getValue(incomingString, ',', 6);
      String intTotalLEDs = getValue(incomingString, ',',7);

      for (int a = intLowerOne.toInt(); a < intUpperOne.toInt(); a++) {
        for (int b = intLowerTwo.toInt(); b < intUpperTwo.toInt(); b++) {
          if (count < intTotalLEDs.toInt()) {
            LedSign::Set(b, a, 1);
            delay(delay_before.toInt());
            takePicture();
            delay(delay_after.toInt());
            LedSign::Set(b, a, 0);

            count += 1;
          }
          else {
            break;
          }
        }
      }
    }
  }
}
