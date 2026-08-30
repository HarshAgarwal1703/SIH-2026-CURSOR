#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ---------------- PIN DEFINITIONS ----------------
#define DHTPIN 4
#define ONE_WIRE_BUS 5
#define RELAY_PIN 13
#define POT_PIN 34
#define LED_PIN 27
#define ACS_PIN 35
#define DHTTYPE DHT22

// ---------------- OBJECTS ----------------
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ---------------- TIMER VARIABLES ----------------
unsigned long relayActivationTime = 0;
bool relayActive = false;
const unsigned long RELAY_HOLD_TIME = 5000;

unsigned long ledActivationTime = 0;
bool ledActive = false;
const unsigned long LED_HOLD_TIME = 5000;

unsigned long pfUpdateTime = 0;
float currentPf = 0.0;
const unsigned long PF_UPDATE_INTERVAL = 2000;

void setup() {

  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, LOW);

  lcd.init();
  lcd.backlight();

  dht.begin();
  sensors.begin();
  sensors.setResolution(9);

  lcd.setCursor(0,0);
  lcd.print("System Starting");
  delay(2000);
  lcd.clear();
}

void loop() {

  // ---------------- LOAD % ----------------
  int potValue = analogRead(POT_PIN);
  int loadPercent = map(potValue,0,4095,0,100);
  loadPercent = constrain(loadPercent,0,100);

  // ---------------- POWER FACTOR ----------------
  if(millis()-pfUpdateTime >= PF_UPDATE_INTERVAL){

    pfUpdateTime = millis();

    float basePf = loadPercent / 100.0;
    float offset = random(20,51)/1000.0;

    if(random(0,2)==0) offset = -offset;

    currentPf = constrain(basePf + offset,0.0,1.0);
  }

  // ---------------- ACS712 LOAD CURRENT ----------------
  float espVoltage = 0;

  for(int i=0;i<100;i++){
    espVoltage += (analogRead(ACS_PIN)/4095.0)*3.3;
  }

  espVoltage /= 100.0;

  float acsVoltage = espVoltage * 1.5;

  float loadCurrent = (acsVoltage - 2.5)/0.100;

  if(abs(loadCurrent)<0.15)
      loadCurrent = 0;

  // ---------------- DHT22 ----------------
  float humidity = dht.readHumidity();
  float airTemp = dht.readTemperature();

  // ---------------- DS18B20 ----------------
  sensors.requestTemperatures();
  float oilTemp = sensors.getTempCByIndex(0);

  // ---------------- RELAY ----------------
  bool tempHigh = (airTemp>40.0)||(oilTemp>39.5);

  if(tempHigh){

    if(!relayActive){

      relayActive = true;
      relayActivationTime = millis();
      digitalWrite(RELAY_PIN,HIGH);
    }
  }
  else{

    if(relayActive && millis()-relayActivationTime>=RELAY_HOLD_TIME){

      relayActive=false;
      digitalWrite(RELAY_PIN,LOW);
    }
  }

  // ---------------- LED ----------------
  bool highLoad = loadPercent>75;

  if(highLoad){

    if(!ledActive){

      ledActive=true;
      ledActivationTime=millis();
      digitalWrite(LED_PIN,HIGH);
    }
  }
  else{

    if(ledActive && millis()-ledActivationTime>=LED_HOLD_TIME){

      ledActive=false;
      digitalWrite(LED_PIN,LOW);
    }
  }

  // ---------------- LCD ----------------
  lcd.setCursor(0,0);
  lcd.print("T:");
  lcd.print(oilTemp,1);
  lcd.print("C ");

  lcd.setCursor(9,0);
  lcd.print("L:");
  lcd.print(loadPercent);
  lcd.print("% ");

  lcd.setCursor(0,1);
  lcd.print("PF:");
  lcd.print(currentPf,2);

  lcd.setCursor(8,1);
  lcd.print("LC:");
  lcd.print(abs(loadCurrent),1);
  lcd.print(" ");

  // ---------------- SERIAL OUTPUT FOR PYTHON ----------------
  // Format:
  // humidity,current,load,loadCurrent,powerFactor

  Serial.print(humidity,1);
  Serial.print(",");

  Serial.print(abs(loadCurrent),2);
  Serial.print(",");

  Serial.print(loadPercent);
  Serial.print(",");

  Serial.print(abs(loadCurrent),2);
  Serial.print(",");

  Serial.println(currentPf,2);

  delay(500);
}