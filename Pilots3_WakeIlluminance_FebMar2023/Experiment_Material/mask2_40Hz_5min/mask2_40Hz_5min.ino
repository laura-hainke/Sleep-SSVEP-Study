int LEDs = 13; // LEDs on pin 13
int trigger = 2; // Trigger on pin 2

int k = 0;
int t = 0;

int ON_time = 12; // 
int OFF_time = 13; // in milliseconds

// the setup function runs once when you press reset or power the board
void setup() {//
  pinMode(LEDs, OUTPUT); // Defining pin as OUTPUT Pin.
  pinMode(trigger, OUTPUT); // Defining pin as OUTPUT Pin.
}

// the loop function runs over and over again forever
void loop() {

  

  // run flicker for 5 min
  t = 0;
  while (t < 300) {
    
    k = 0;
    
    digitalWrite(trigger, HIGH);
    
    while (k < 40) { // loop 40 Hz flicker 40 times to make one second
      digitalWrite(LEDs, HIGH);   // turn the LED on (HIGH is the voltage level)
      delay(ON_time);                      // wait
      digitalWrite(LEDs, LOW);    // turn the LED off by making the voltage LOW
      delay(OFF_time);                     // wait
      if (k == 0) { // trigger off after one cycle
        digitalWrite(trigger, LOW);
      }
      k++;
      
    }
    
    t++;
  }

  
}
