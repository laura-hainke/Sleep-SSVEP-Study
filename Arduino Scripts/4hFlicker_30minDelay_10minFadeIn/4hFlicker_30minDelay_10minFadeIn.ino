

int LEDs = 12; // LEDs on pin 12
int trigger = 4; // Trigger on pin 4
int k = 0;
int t = 0;

unsigned int ON_time = 10; // for fade in duty cycle, in microseconds
int OFF_time = 25; // in milliseconds


// the setup function runs once when you press reset or power the board
void setup() {//
  pinMode(LEDs, OUTPUT); // Defining pin as OUTPUT Pin.
  pinMode(trigger, OUTPUT); // Defining pin as OUTPUT Pin.

  // wait 30 mins (1800 seconds)
  t = 0;

  while (t < 1800) {
    delay(1000); // wait one second
    t++;
  }

}


// the loop function runs over and over again forever
void loop() {
  
  // fade in duty cycle

  t = 0;

  while (t < 600) { // loop for 10 mins, increase the duty cycle by 20 microseconds each second; no triggers

    k = 0;

    while (k < 40) { // loop 40 Hz flicker for one second

      digitalWrite(LEDs, HIGH);   // turn the LED on (HIGH is the voltage level)

      delayMicroseconds(ON_time); // wait

      digitalWrite(LEDs, LOW);    // turn the LED off by making the voltage LOW

      delay(OFF_time);            //  wait

      k++;

    }
    ON_time = ON_time + 20; // increase the duty cycle by 20 microseconds
    OFF_time =  25 - (ON_time / 1000);      // convert to milliseconds, because delayMicroseconds doesn't work for values above 16000
    t++;
  }


  // run flicker for 4 hours (14400 seconds), with triggers

  t = 0;

  while (t < 14400) {

    k = 0;
    digitalWrite(trigger, HIGH);

    while (k < 40) { // loop 40 Hz flicker 40 times to make one second

      digitalWrite(LEDs, HIGH);   // turn the LED on (HIGH is the voltage level)

      delay(12);                       // wait
      
      digitalWrite(LEDs, LOW);    // turn the LED off by making the voltage LOW

      delay(13);                       // wait

      if (k == 0) { // trigger off after one cycle
        digitalWrite(trigger, LOW);
      }

      k++;

    }

    t++;
  }


  
}
