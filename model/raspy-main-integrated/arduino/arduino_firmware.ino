/*
 * Arduino Nano Lab Attendance System
 * MERGED STABLE VERSION - RAM OPTIMIZED
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad_I2C.h>
#include <Keypad.h>
#include <ArduinoJson.h>

#define LCD_ADDR 0x27
#define KEYPAD_ADDR 0x20
#define TOUCH_PIN 7
#define RELAY_PIN 3
#define EMERGENCY_PIN 4

LiquidCrystal_I2C lcd(LCD_ADDR, 20, 4);

const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'D','C','B','A'},
  {'#','9','6','3'},
  {'0','8','5','2'},
  {'*','7','4','1'}
};

byte rowPins[ROWS] = {4,5,6,7};
byte colPins[COLS] = {0,1,2,3};

Keypad_I2C keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS, KEYPAD_ADDR);

StaticJsonDocument<512> jsonDoc;

unsigned long lastTouchTime = 0;
unsigned long lastEmergencyTime = 0;
unsigned long relayStart = 0;
unsigned long relayDuration = 0;

bool relayActive = false;
bool lastTouchState = LOW;

const unsigned long DEBOUNCE = 200;

// ================= LCD CENTER =================
void lcdPrintCentered(const String& s, int row) {
  int len = min((int)s.length(), 20);
  int pad = (20 - len) / 2;
  lcd.setCursor(0, row);
  for (int i = 0; i < pad; i++) lcd.print(' ');
  lcd.print(s.substring(0, len));
  for (int i = pad + len; i < 20; i++) lcd.print(' ');
}

void lcdShow(const char* l1="", const char* l2="", const char* l3="", const char* l4="") {
  lcd.clear();
  lcdPrintCentered(String(l1), 0);
  lcdPrintCentered(String(l2), 1);
  lcdPrintCentered(String(l3), 2);
  lcdPrintCentered(String(l4), 3);
}

// ================= SEND JSON =================
void sendJson(const char* type,
              const char* k1=NULL, const char* v1=NULL,
              const char* k2=NULL, const char* v2=NULL) {
  jsonDoc.clear();
  jsonDoc["type"] = type;
  if (k1) jsonDoc[k1] = v1;
  if (k2) jsonDoc[k2] = v2;
  serializeJson(jsonDoc, Serial);
  Serial.println();
}

// ================= SEND RELAY ACK =================
void sendRelayAck(const char* action, int duration = 0) {
  jsonDoc.clear();
  jsonDoc["type"] = "ack";
  jsonDoc["device"] = "relay";
  jsonDoc["action"] = action;
  if (duration > 0) jsonDoc["duration"] = duration;
  serializeJson(jsonDoc, Serial);
  Serial.println();
}

// ================= OPEN RELAY =================
void openRelay(int durationSec) {
  Serial.println(F("[DEBUG] Relay OPEN"));       // ← F() macro
  digitalWrite(RELAY_PIN, HIGH);
  relayDuration = ((unsigned long)durationSec) * 1000UL;
  relayStart = millis();
  relayActive = true;
  Serial.print(F("[DEBUG] relayDuration ms: ")); // ← F() macro
  Serial.println(relayDuration);
  sendRelayAck("open", durationSec);
}

// ================= CLOSE RELAY =================
void closeRelay() {
  Serial.println(F("[DEBUG] Relay CLOSE"));      // ← F() macro
  digitalWrite(RELAY_PIN, LOW);
  relayActive = false;
  relayStart = 0;
  relayDuration = 0;
  sendRelayAck("close");
}

// ================= PROCESS COMMAND =================
void processCommand(String input) {

  Serial.print(F("[DEBUG] RX: "));               // ← F() macro
  Serial.println(input);

  jsonDoc.clear();
  DeserializationError err = deserializeJson(jsonDoc, input);

  if (err) {
    Serial.print(F("[DEBUG] JSON ERR: "));        // ← F() macro
    Serial.println(err.c_str());
    return;
  }

  const char* type = jsonDoc["type"];
  if (!type) return;

  // ===== DISPLAY =====
  if (strcmp(type, "display") == 0) {
    JsonArray lines = jsonDoc["lines"];
    lcdShow(
      lines[0] | "",
      lines[1] | "",
      lines[2] | "",
      lines[3] | ""
    );
  }

  // ===== ACTUATOR =====
  else if (strcmp(type, "actuator") == 0) {
    const char* device = jsonDoc["device"];
    const char* action = jsonDoc["action"];

    if (!device || !action) return;

    if (strcmp(device, "relay") == 0) {
      if (strcmp(action, "open") == 0) {
        int duration = jsonDoc["duration"] | 5;
        Serial.print(F("[DEBUG] Duration: "));   // ← F() macro
        Serial.println(duration);
        openRelay(duration);
      }
      else if (strcmp(action, "close") == 0) {
        closeRelay();
      }
    }
  }
}

// ================= SETUP =================
void setup() {

  Serial.begin(115200);
  Serial.setTimeout(50); // ← tetap 50, bukan 500

  pinMode(TOUCH_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(EMERGENCY_PIN, INPUT_PULLUP);
  digitalWrite(RELAY_PIN, LOW);

  Wire.begin();
  delay(100);

  lcd.init();
  lcd.backlight();

  lcdShow("Arduino Ready", "Waiting Pi...", "", "");

  keypad.begin();
  delay(500);

  sendJson("system", "event", "boot");
}

// ================= LOOP =================
void loop() {

  unsigned long now = millis();

  // ===== SERIAL RECEIVE =====
  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming.length() > 0) {
      processCommand(incoming);
    }
  }

  // ===== TOUCH =====
  bool touch = digitalRead(TOUCH_PIN);
  if (touch == HIGH && lastTouchState == LOW &&
      (now - lastTouchTime > DEBOUNCE)) {
    sendJson("input", "source", "touch", "state", "on");
    lastTouchTime = now;
  }
  lastTouchState = touch;

  // ===== EMERGENCY =====
  if (digitalRead(EMERGENCY_PIN) == LOW &&
      (now - lastEmergencyTime > 800)) {
    sendJson("event", "name", "emergency", "state", "pressed");
    lastEmergencyTime = now;
  }

  // ===== RELAY TIMER =====
  if (relayActive) {
    unsigned long elapsed = millis() - relayStart;
    if (elapsed >= relayDuration) {
      Serial.println(F("[DEBUG] Relay AUTO CLOSE")); // ← F() macro
      digitalWrite(RELAY_PIN, LOW);
      relayActive = false;
      relayStart = 0;
      relayDuration = 0;
      sendRelayAck("timeout-close");
    }
  }

  // ===== KEYPAD =====
  char key = keypad.getKey();
  if (key) {
    char k[2] = {key, '\0'};
    sendJson("input", "source", "keypad", "key", k);
  }
}

code arduino di folder dipa
