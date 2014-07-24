#include <LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

const int buttonPins[] = {6, 7, 8, 9, 10, 13};
const int numButtons = 6;

int buttonState[numButtons];

void setup() {
  Serial.begin(9600);
  
  lcd.begin(16, 2);
  
  int count;
  for (count = 0; count < numButtons; count++) {
    pinMode(buttonPins[count], INPUT);
  }
}

void loadData() {
  lcd.setCursor(0, 0);
  
  while (Serial.available() > 0) {
    lcd.clear();
    
    String line1 = Serial.readStringUntil('|');
    
    lcd.print(line1);
    
    lcd.setCursor(0, 1);
    String line2 = Serial.readStringUntil(';');
    
    lcd.print(line2);
  }
}

void loop() {
  int shift = digitalRead(buttonPins[0]);
  
  loadData();
  
  lcd.setCursor(15, 1);
  if (shift == HIGH) {
    lcd.print("S");
  } else {
    lcd.print("N");
  }
  
  int count;
  for (count = 1; count < numButtons; count++) {
    int currentState = digitalRead(buttonPins[count]);
    
    if (buttonState[count] != currentState && currentState == HIGH) {
      if (shift == HIGH) {
        Serial.println(count * 10);
      } else {
        Serial.println(count);
      }
    }
    
    buttonState[count] = currentState;
  }
  
  delay(5);
}
