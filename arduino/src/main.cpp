#include <Arduino.h>

const int box_pins[] = {2, 3, 4, 5, 6, 7, 8, 9};

void open(int);

void setup()
{
  // immediately setup outputs and set all to 1 (because the relay is active low)
  for (int i = 0; i < 8; i++)
  {
    pinMode(box_pins[i], OUTPUT);
    digitalWrite(box_pins[i], 1);
  }

  // start serial communication
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available() > 0) // if there was a message received
  {
    String line = Serial.readStringUntil('\n'); // get the full message (1 line)
    int box = line.toInt();                     // convert to int for box number
    open(box);                                  // actually open the box
  }
}

void open(int box)
{
  if (box < 0 || box > 7) // if the box number is invalid
  {
    // Serial.println("error");
    // just ignore the request
    return;
  }

  digitalWrite(box_pins[box], 0); // set the pin to 0 to activate the relay (and box lock solenoid)
  delay(500);                         // wait for half a second
  digitalWrite(box_pins[box], 1); // set the pin back to 1 to deactivate
}