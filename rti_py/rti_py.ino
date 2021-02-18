#include <avr/pgmspace.h>
#include <Charliplexing.h>

String incomingString;
String conditions;
String led;
int count;


String getValue(String data, char separator, int index) // function that parses the setup string to separate out variables from a comma delimited list
{
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

void setup() {
  pinMode(A0, OUTPUT);                                  // set analogue pin A0 to output mode to use for IR LED
  Serial.begin(9600);                                   // start serial communication
  LedSign::Init();                                      // initiate the LOL shield
}

// sets the pulse of the IR signal.
void pulseON(int pulseTime)
{
  unsigned long endPulse = micros() + pulseTime;        // create the microseconds to pulse for
  while ( micros() < endPulse)
  {
    digitalWrite(A0, HIGH);                             // turn IR on
    delayMicroseconds(13);                              // half the clock cycle for 38Khz (26.32×10-6s) - e.g. the 'on' part of our wave
    digitalWrite(A0, LOW);                              // turn IR off
    delayMicroseconds(13);                              // delay for the other half of the cycle to generate wave/ oscillation
  }

}

void pulseOFF(unsigned long startDelay)
{
  unsigned long endDelay = micros() + startDelay;       // create the microseconds to delay for
  while (micros() < endDelay);
}

void takePicture()
{
  for (int i = 0; i < 2; i++)
  {
    pulseON(2000);                                      // pulse for 2000 uS (Microseconds)
    pulseOFF(27850);                                    // turn pulse off for 27850 us
    pulseON(390);                                       // and so on
    pulseOFF(1580);
    pulseON(410);
    pulseOFF(3580);
    pulseON(400);
    pulseOFF(63200);
  }                                                     // loop the signal twice.
}

void loop()
{
  uint8_t i;
  if (Serial.available() > 0)
  {
    incomingString = Serial.readString();
    String instructionByte = getValue(incomingString,',',0); 
    Serial.print("I received: ");
    Serial.print(incomingString);
    Serial.print(" the instructionByte was: ");
    Serial.print(instructionByte);

    if (instructionByte == "L")
    {
      Serial.print("I should be lighting an LED right now!");
      LedSign::Set(3, 0, 1);
      delay(60000);
      LedSign::Set(3, 0, 0);
    }
    else if (instructionByte == "T")
    {
      String led_x = getValue(incomingString, ',', 1);
      String led_y = getValue(incomingString, ',', 2);
      String led_delay = getValue(incomingString, ',', 3);

      LedSign::Set(led_x.toInt(), led_y.toInt(), 1);

      delay(led_delay.toInt()*1000);

      LedSign::Set(led_x.toInt(), led_y.toInt(), 0);
    }
    else if (instructionByte == "C")
    {
      String delay_before = getValue(incomingString, ',', 1);
      String delay_after = getValue(incomingString, ',', 2);
      String intLowerOne = getValue(incomingString, ',', 3);
      String intUpperOne = getValue(incomingString, ',', 4);
      String intLowerTwo = getValue(incomingString, ',', 5);
      String intUpperTwo = getValue(incomingString, ',', 6);
      String intTotalLEDs = getValue(incomingString, ',',7);

      for (int a = intLowerOne.toInt(); a < intUpperOne.toInt(); a++)
      {
        for (int b = intLowerTwo.toInt(); b < intUpperTwo.toInt(); b++)
        {
          if (count < intTotalLEDs.toInt())
          {
            LedSign::Set(b, a, 1);
            delay(delay_before.toInt());
            takePicture();
            delay(delay_after.toInt());
            LedSign::Set(b, a, 0);

            count += 1;
          }
          else
          {
            break;
          }
        }
      }
    }
  }
}
