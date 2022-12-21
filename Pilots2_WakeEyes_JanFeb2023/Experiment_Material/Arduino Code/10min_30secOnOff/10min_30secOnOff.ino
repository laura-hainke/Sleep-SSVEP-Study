

int LEDs = 12; // LEDs on pin 12
int trigger = 4; // Trigger on pin 4
int k = 0;
int t = 0;

unsigned int ON_time = 10; // for fade in duty cycle, in microseconds
int OFF_time = 25; // in milliseconds
int cycle_ctr = 0; // counter for stimulation cycles


// the setup function runs once when you press reset or power the board
void setup() {//
  pinMode(LEDs, OUTPUT); // Defining pin as OUTPUT Pin.
  pinMode(trigger, OUTPUT); // Defining pin as OUTPUT Pin.

  delay(5000); // wait 5 seconds after button press

}


void loop() {

  // repeat cycle of 30 sec on / 30 sec off, 10 times
  while (cycle_ctr < 10) { 

    // run flicker for 30 sec
  
    t = 0;
  
    while (t < 30) {
  
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

    // wait for 30 sec

    delay(30000);
    
   cycle_ctr++;
  }
  
}
