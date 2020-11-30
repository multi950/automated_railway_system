#include <ESP8266WiFi.h>
#include <ros.h>
#include <std_msgs/String.h>
#include <std_msgs/Int16.h>
#include <std_msgs/Float64.h>
#include <SoftwareSerial.h>
//////////////////////
// WiFi Definitions //
//////////////////////
const char* ssid = "Ras_the_Moose";
const char* password = "1234qwer";

IPAddress server(192, 168, 43, 232); // ip of your ROS server
IPAddress ip_address;
int status = WL_IDLE_STATUS;

WiFiClient client;

SoftwareSerial arduino_connection(3, 1); // RX, TX

class WiFiHardware {

  public:
  WiFiHardware() {};

  void init() {
    // do your initialization here. this probably includes TCP server/client setup
    client.connect(server, 11411);
  }

  // read a byte from the serial port. -1 = failure
  int read() {
    // implement this method so that it reads a byte from the TCP connection and returns it
    //  you may return -1 is there is an error; for example if the TCP connection is not open
    return client.read();         //will return -1 when it will works
  }

  // write data to the connection to ROS
  void write(uint8_t* data, int length) {
    // implement this so that it takes the arguments and writes or prints them to the TCP connection
    for(int i=0; i<length; i++)
      client.write(data[i]);
  }

  // returns milliseconds since start of program
  unsigned long time() {
     return millis(); // easy; did this one for you
  }
};



void chatterCallback(const std_msgs::String& msg) {
  //Serial.println(msg.data);
    arduino_connection.write(msg.data);

}

ros::Subscriber<std_msgs::String> sub("message", &chatterCallback);
ros::NodeHandle_<WiFiHardware> nh;

void setupWiFi()
{
  WiFi.begin(ssid, password);
  //Serial.print("\nConnecting to "); //Serial.println(ssid);
  uint8_t i = 0;
  while (WiFi.status() != WL_CONNECTED && i++ < 20) delay(500);
  if(i == 21){
    //Serial.print("Could not connect to"); //Serial.println(ssid);
    while(1) delay(500);
  }
  //Serial.print("Ready! Use ");
  //Serial.print(WiFi.localIP());
  //Serial.println(" to access client");
}

void setup() {
  //Serial.begin(115200);
  arduino_connection.begin(38400);
  setupWiFi();
  delay(2000);
  nh.initNode();
  nh.subscribe(sub);
}

void loop() {
  nh.spinOnce();
  delay(1);
}
