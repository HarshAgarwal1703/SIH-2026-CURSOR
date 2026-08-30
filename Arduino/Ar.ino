#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pin Definitions
#define DHTPIN 4
#define ONE_WIRE_BUS 5
#define RELAY_PIN 13
#define POT_PIN 34     
#define LED_PIN 27 
#define ACS_PIN 35         
#define DHTTYPE DHT22

// Initialize Components
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Timer Variables ---
unsigned long relayActivationTime = 0;
bool relayActive = false;
const unsigned long RELAY_HOLD_TIME = 5000; 

unsigned long ledActivationTime = 0;
bool ledActive = false;
const unsigned long LED_HOLD_TIME = 5000;   

// --- Power Factor Variables ---
unsigned long pfUpdateTime = 0;
float currentPf = 0.0;
const unsigned long PF_UPDATE_INTERVAL = 2000; 

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  lcd.init();
  lcd.backlight();
  dht.begin();
  sensors.begin();
  sensors.setResolution(9); 
  
  lcd.setCursor(0, 0);
  lcd.print("System Starting");
  delay(2000);
  lcd.clear();
}

void loop() {
  // 1. Read Potentiometer Load
  int potValue = analogRead(POT_PIN);
  int loadPercent = map(potValue, 0, 4095, 0, 100);
  loadPercent = constrain(loadPercent, 0, 100); 

  // --- 2. Power Factor Logic ---
  if (millis() - pfUpdateTime >= PF_UPDATE_INTERVAL) {
    pfUpdateTime = millis();
    float basePf = loadPercent / 100.0;
    float offset = random(20, 51) / 1000.0;
    
    if (random(0, 2) == 0) offset = -offset;
    
    currentPf = basePf + offset;
    if (currentPf > 1.00) currentPf = 1.00;
    if (currentPf < 0.00) currentPf = 0.00;
  }

  // --- 3. ACS712 Current Reading ---
  float espVoltage = 0.0;
  for(int i = 0; i < 100; i++) {
    espVoltage += (analogRead(ACS_PIN) / 4095.0) * 3.3;
  }
  espVoltage = espVoltage / 100.0; 
  
  float acsVoltage = espVoltage * 1.5; 
  float currentAmps = (acsVoltage - 2.5) / 0.100; 
  if (abs(currentAmps) < 0.15) currentAmps = 0.0;

  // 4. Read DHT22 (Kept for background logic)
  float dhtHum = dht.readHumidity(); 
  float dhtTemp = dht.readTemperature(); 
  
  // 5. Read DS18B20 
  sensors.requestTemperatures(); 
  float dsTemp = sensors.getTempCByIndex(0);

  // --- Independent Logic 1: Temperature Relay ---
  bool tempConditionsMet = (dhtTemp > 40.0) || (dsTemp > 39.5);
  
  if (tempConditionsMet) {
    if (!relayActive) {
      relayActive = true;
      relayActivationTime = millis(); 
      digitalWrite(RELAY_PIN, HIGH);
    }
  } else {
    if (relayActive && (millis() - relayActivationTime >= RELAY_HOLD_TIME)) {
      relayActive = false;
      digitalWrite(RELAY_PIN, LOW);
    }
  }

  // --- Independent Logic 2: Load LED ---
  bool loadConditionMet = (loadPercent > 75);
  
  if (loadConditionMet) {
    if (!ledActive) {
      ledActive = true;
      ledActivationTime = millis(); 
      digitalWrite(LED_PIN, HIGH);
    }
  } else {
    if (ledActive && (millis() - ledActivationTime >= LED_HOLD_TIME)) {
      ledActive = false;
      digitalWrite(LED_PIN, LOW);
    }
  }

  // --- LCD Formatting ---
  // Row 0, Left: DS18B20 Temperature
  lcd.setCursor(0, 0);
  lcd.print("T:");
  if (dsTemp == DEVICE_DISCONNECTED_C) lcd.print("Err ");
  else {
    lcd.print(dsTemp, 1);
    lcd.print("C ");
  }
  
  // Row 0, Right: Load Percentage
  lcd.setCursor(9, 0);
  lcd.print("L:");
  lcd.print(loadPercent);
  lcd.print("%  "); 

  // Row 1, Left: Power Factor
  lcd.setCursor(0, 1);
  lcd.print("PF:");
  lcd.print(currentPf, 2);
  lcd.print(" ");

  // Row 1, Right: ACS712 Amperage
  lcd.setCursor(8, 1);
  lcd.print("LC:");
  lcd.print(abs(currentAmps), 1);
  lcd.print("   ");

  delay(250); 
}