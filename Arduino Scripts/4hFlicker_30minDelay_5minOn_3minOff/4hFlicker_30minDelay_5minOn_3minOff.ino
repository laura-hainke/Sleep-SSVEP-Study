

int LEDs = 12; // LEDs on pin 12
int trigger = 4; // Trigger on pin 4
int k = 0;
int t = 0;

unsigned int ON_time = 50; // for fade in duty cycle, in microseconds
int OFF_time = 25; // in milliseconds
int cycle_ctr = 0; // counter for stimulation cycles


// the setup function runs once when you press reset or power the board
void setup() {//
  pinMode(LEDs, OUTPUT); // Defining pin as OUTPUT Pin.
  pinMode(trigger, OUTPUT); // Defining pin as OUTPUT Pin.

  // wait 30 mins (1800 seconds) - initial delay to allow for sleep onset before stimulation start
  t = 0;
  
  while (t < 1800) {
    delay(1000); // wait one second
    t++;
  }

}


// the loop function runs over and over again forever
// for 4:20 hours, alternate on and off periods (with fade-in and fade-out)
void loop() {

  while (cycle_ctr < 42) {
  
    // fade in duty cycle, no triggers
  
    t = 0;
  
    ON_time = 50;
  
    while (t < 70) { // loop for 1:10 min, increase the duty cycle each second
  
      k = 0;
  
      while (k < 40) { // loop 40 Hz flicker for one second
  
        digitalWrite(LEDs, HIGH);   // turn the LED on (HIGH is the voltage level)
  
        delayMicroseconds(ON_time); // wait
  
        digitalWrite(LEDs, LOW);    // turn the LED off by making the voltage LOW
  
        delay(OFF_time);            //  wait
  
        k++;
  
      }
  
      if (ON_time < 2000) { // in first 20 increase cycles, increase by 100 microseconds only
        ON_time = ON_time + 100; // increase the duty cycle by 100 microseconds
      } else {
        ON_time = ON_time + 200; // increase the duty cycle by 200 microseconds
      }
      
      OFF_time =  25 - (ON_time / 1000); // convert to milliseconds, because delayMicroseconds doesn't work for values above 16000
      t++;
    }
  
  
  
    // run flicker for 5 min (300 seconds), with triggers
  
    t = 0;
  
    while (t < 300) {
  
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
  
  
    // fade out duty cycle, no triggers
  
    t = 0;
  
    ON_time = 12000;
  
    while (t < 70) { // loop for 1:20 min, decrease the duty cycle each second
  
      k = 0;
  
      while (k < 40) { // loop 40 Hz flicker for one second
  
        digitalWrite(LEDs, HIGH);   // turn the LED on (HIGH is the voltage level)
  
        delayMicroseconds(ON_time);                       // wait
  
        digitalWrite(LEDs, LOW);    // turn the LED off by making the voltage LOW
  
        delay(OFF_time);            //  wait
  
        k++;
  
      }
      
      if (ON_time < 2000) { // in last 20 decrease cycles, decrease by 100 microseconds only
        ON_time = ON_time - 100; // decrease the duty cycle by 100 microseconds
      } else {
        ON_time = ON_time - 200; // decrease the duty cycle by 200 microseconds
      }
        
      OFF_time =  25 - (ON_time / 1000);      // convert to milliseconds, because delayMicroseconds doesn't work for values above 16000
      t++;
    }
  
  
    // wait for 3 min (180 seconds)
  
    t = 0;
  
    while (t < 180) {
      delay(1000); // wait one second
      t++;
    }

  cycle_ctr++;
  }
  
}
