

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

}


// the loop function runs over and over again forever
void loop() {
  
  // run flicker for 4.5 hours (16200 seconds), with triggers

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
