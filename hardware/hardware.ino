#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "";
const char* password = "";

const char* mqtt_server = "";
const char* mqtt_username = "";
const char* mqtt_password = "";

LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void scrollMessage(String strlines[], int length, int delayTime) {

  String copy[length];
  for (int i = 0; i < length; ++i) {
    copy[i] = strlines[i].substring(0, strlines[i].length());
  }

  int largest = 0;
  for (int i = 0; i < length; ++i) {
    if (copy[i].length() > strlines[largest].length()) largest = i;
  }

  for (int i = 0; i < length; ++i) {
    int length_diff = 0;
    if (largest != i) {
      length_diff = strlines[largest].length() - copy[i].length();
      for (int j = 0; j < length_diff; ++j) {
        copy[i] += ' ';
      }
    }
  }

  for (int i = 0; i < 16; i++) {
    copy[0] = " " + copy[0];
    copy[1] = " " + copy[1];
  } 
  copy[0] = copy[0] + " "; 
  copy[1] = copy[1] + " "; 

  for (int position = 0; position < copy[0].length(); position++) {
    lcd.setCursor(0, 0);
    lcd.print(copy[0].substring(position, position + 16));
    lcd.setCursor(0, 1);
    lcd.print(copy[1].substring(position, position + 16));
    delay(delayTime);
  }

}

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  lcd.clear();
  lcd.setCursor(0, 0);
  payload[length] = '\0';

  String strlines[2];
  unsigned int line_no = 0;

  for (unsigned int i = 0; i < length; ++i) {
    if ((char)payload[i] == ',') {
      line_no += 1;
    } else {
      strlines[line_no] += (char)payload[i];
    }
  }

  lcd.clear();
  lcd.backlight();
  for (int i = 0; i < 3; ++i) {
    tone(D5, 2200);
    digitalWrite(D8, HIGH);
    delay(1000);
    noTone(D5);
    digitalWrite(D8, LOW);
    delay(1000);
    scrollMessage(strlines, 2, 500);
  }
  lcd.noBacklight();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      // ... and resubscribe
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(BUILTIN_LED, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D8, OUTPUT);
  lcd.init();
  lcd.clear();
  lcd.backlight();
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
