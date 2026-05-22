/*
  Lab Robotika 2025 - Arduino Nano Firmware
  Integrated Attendance System
  
  Hardware:
  - Arduino Nano (ATmega328P)
  - 16x4 I2C LCD Display (0x27)
  - 1602 LCD with PCF8574 I2C backpack
  - Touch Sensor (Pin A0)
  - 4x4 Keypad (Matrix)
  - Emergency Button (Pin D2)
  - Relay Module (Pin D13)
  - Serial communication with Raspberry Pi @ 115200 baud
  
  Protocol: JSON via Serial UART
  
  Expected messages from RPi:
  {
    "type": "display",
    "lines": ["Line 0", "Line 1", "Line 2", "Line 3"]
  }
  {
    "type": "actuator",
    "device": "relay",
    "action": "open|close",
    "duration": 5
  }
  
  Messages sent to RPi:
  {"type": "system", "event": "boot"}
  {"type": "input", "source": "touch", "state": "on"}
  {"type": "input", "source": "keypad", "key": "A"}
  {"type": "event", "name": "emergency", "state": "pressed"}
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>
#include <ArduinoJson.h>

// ========== PIN DEFINITIONS ==========
#define TOUCH_PIN      A0
#define EMERGENCY_PIN   2
#define RELAY_PIN      13
#define BACKLIGHT_PIN  11  // PWM for backlight brightness

// ========== LCD Configuration ==========
// 16x4 LCD with I2C address 0x27
LiquidCrystal_I2C lcd(0x27, 20, 4);

// ========== KEYPAD Configuration ==========
const byte ROWS = 4;
const byte COLS = 4;

char hexaKeys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

// Adjust pins based on your wiring
byte rowPins[ROWS] = {12, 11, 10, 9};        // R1, R2, R3, R4
byte colPins[COLS] = {8, 7, 6, 5};           // C1, C2, C3, C4

Keypad keypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);

// ========== STATE VARIABLES ==========
unsigned long lastTouchTime = 0;
unsigned long lastEmergencyTime = 0;
unsigned long relayStartTime = 0;
unsigned long relayDuration = 0;
bool relayActive = false;
bool touchActive = false;

// JSON buffer
StaticJsonDocument<256> jsonDoc;

void setup() {
  Serial.begin(115200);
  delay(500);  // Wait for serial to stabilize
  
  // Initialize pins
  pinMode(TOUCH_PIN, INPUT);
  pinMode(EMERGENCY_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BACKLIGHT_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  
  // Initialize LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  lcd.setCursor(0, 1);
  lcd.print("Lab Robotika 2025");
  
  delay(1000);
  
  // Send boot signal to RPi
  sendBootSignal();
  
  // Clear LCD
  lcd.clear();
  displayDefault();
}

void loop() {
  // Handle serial commands from RPi
  if (Serial.available()) {
    handleSerialInput();
  }
  
  // Handle keypad input
  handleKeypadInput();
  
  // Handle touch sensor
  handleTouchSensor();
  
  // Handle emergency button
  handleEmergencyButton();
  
  // Handle relay timeout
  handleRelayTimeout();
  
  delay(10);
}

// ========== SERIAL COMMUNICATION ==========

void sendBootSignal() {
  DynamicJsonDocument doc(128);
  doc["type"] = "system";
  doc["event"] = "boot";
  serializeJson(doc, Serial);
  Serial.println();
}

void handleSerialInput() {
  String input = Serial.readStringUntil('\n');
  input.trim();
  
  if (input.length() == 0) return;
  
  // Parse JSON from RPi
  DeserializationError error = deserializeJson(jsonDoc, input);
  
  if (error) {
    Serial.print("{\"error\": \"JSON parse failed: ");
    Serial.print(error.c_str());
    Serial.println("\"}");
    return;
  }
  
  String msgType = jsonDoc["type"];
  
  if (msgType == "display") {
    handleDisplayCommand();
  }
  else if (msgType == "actuator") {
    handleActuatorCommand();
  }
  else if (msgType == "ping") {
    sendPongResponse();
  }
}

void sendPongResponse() {
  DynamicJsonDocument doc(64);
  doc["type"] = "pong";
  doc["time"] = millis();
  serializeJson(doc, Serial);
  Serial.println();
}

void handleDisplayCommand() {
  // Clear LCD
  lcd.clear();
  
  // Display 4 lines
  for (int i = 0; i < 4; i++) {
    if (jsonDoc["lines"][i] != nullptr) {
      String line = jsonDoc["lines"][i].as<String>();
      lcd.setCursor(0, i);
      
      // Truncate to 20 chars (adjust for your LCD width)
      if (line.length() > 20) {
        line = line.substring(0, 20);
      }
      
      lcd.print(line);
    }
  }
}

void handleActuatorCommand() {
  String device = jsonDoc["device"];
  String action = jsonDoc["action"];
  
  if (device == "relay") {
    if (action == "open") {
      openRelay();
      relayDuration = jsonDoc["duration"] | 5;  // Default 5 seconds
      relayStartTime = millis();
      relayActive = true;
    }
    else if (action == "close") {
      closeRelay();
      relayActive = false;
    }
  }
}

// ========== KEYPAD HANDLER ==========

void handleKeypadInput() {
  char key = keypad.getKey();
  
  if (key) {
    // Debounce: ignore rapid repeats
    static unsigned long lastKeyTime = 0;
    if (millis() - lastKeyTime < 50) return;
    lastKeyTime = millis();
    
    // Send to RPi
    DynamicJsonDocument doc(128);
    doc["type"] = "input";
    doc["source"] = "keypad";
    char keyStr[2] = {key, '\0'};
    doc["key"] = keyStr;
    serializeJson(doc, Serial);
    Serial.println();
  }
}

// ========== TOUCH SENSOR HANDLER ==========

void handleTouchSensor() {
  int touchValue = analogRead(TOUCH_PIN);
  bool touched = (touchValue < 512);  // Adjust threshold based on calibration
  
  // Debounce
  if (touched && !touchActive) {
    if (millis() - lastTouchTime > 500) {  // 500ms debounce
      touchActive = true;
      lastTouchTime = millis();
      
      // Send to RPi
      DynamicJsonDocument doc(128);
      doc["type"] = "input";
      doc["source"] = "touch";
      doc["state"] = "on";
      serializeJson(doc, Serial);
      Serial.println();
    }
  }
  else if (!touched && touchActive) {
    touchActive = false;
  }
}

// ========== EMERGENCY BUTTON HANDLER ==========

void handleEmergencyButton() {
  // Button active LOW (pulled up)
  int btnState = digitalRead(EMERGENCY_PIN);
  
  if (btnState == LOW) {
    if (millis() - lastEmergencyTime > 500) {  // 500ms debounce
      lastEmergencyTime = millis();
      
      // Send to RPi
      DynamicJsonDocument doc(128);
      doc["type"] = "event";
      doc["name"] = "emergency";
      doc["state"] = "pressed";
      serializeJson(doc, Serial);
      Serial.println();
    }
  }
}

// ========== RELAY CONTROL ==========

void openRelay() {
  digitalWrite(RELAY_PIN, HIGH);
}

void closeRelay() {
  digitalWrite(RELAY_PIN, LOW);
}

void handleRelayTimeout() {
  if (relayActive && (millis() - relayStartTime) >= (relayDuration * 1000UL)) {
    closeRelay();
    relayActive = false;
  }
}

// ========== DISPLAY HELPERS ==========

void displayDefault() {
  lcd.setCursor(0, 0);
  lcd.print("Lab Robotika");
  lcd.setCursor(0, 1);
  lcd.print("Ready");
}
