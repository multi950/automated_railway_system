#include <SoftwareSerial.h>


SoftwareSerial esp_connection(2, 6); // RX, TX

int motorpin1 = 3;
int motorpin2 = 4;
int speedpin = 9;


void setup() 
{
  pinMode(motorpin1, OUTPUT);
  pinMode(motorpin2, OUTPUT);
  pinMode(speedpin, OUTPUT);
  
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  esp_connection.begin(38400);
    while (!Serial) {
     // wait for serial port to connect. Needed for Native USB only
  }
}

void loop() // run over and over
{
  if (esp_connection.available()){

    char input = esp_connection.read();
    
    if(input == 'u'){
      digitalWrite(LED_BUILTIN, HIGH);
      enable_motor(true);
    }else if(input == 'd'){
      digitalWrite(LED_BUILTIN, LOW);
      enable_motor(true);
    } else if(input == 'q'){
      digitalWrite(LED_BUILTIN, LOW);
      turn_motor_off();
    }
    Serial.println("character:");
    Serial.println(input);
  }
    
}

void enable_motor(boolean forward){
if(forward){
  digitalWrite(motorpin1, HIGH);
  digitalWrite(motorpin2, LOW);
  analogWrite(speedpin, 255);
}else {
  digitalWrite(motorpin1, LOW);
  digitalWrite(motorpin2, HIGH);
  analogWrite(speedpin, 255);
}
}
void turn_motor_off(){
  digitalWrite(motorpin1, LOW);
  digitalWrite(motorpin2, LOW);
  analogWrite(speedpin, 0);
}
