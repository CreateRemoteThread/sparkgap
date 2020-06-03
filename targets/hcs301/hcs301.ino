/*
 * hcs301 support thingy
 */

#define PIN_BTN 8     // PB0 (bottom left)
#define PIN_PWM_IN 9  // PB1 (bottom right)
#define PIN_LED 12

// #define PIN_TOGGLE 10

#include <util/delay.h>

unsigned char pewpewpew[128];
unsigned char nextByte = 0;

int toggleMode = 0;
int bitPosn = 0;

void setup() {
  Serial.begin(115200);
  Serial.print("#");
  pinMode(PIN_BTN, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_PWM_IN, INPUT);
  // pinMode(PIN_TOGGLE, OUTPUT);
  bitPosn = 0;
  toggleMode = 0;
  int i = 0;
  for(i = 0;i < 3;i++)
  {
    digitalWrite(PIN_LED,HIGH);
    delay(200);
    digitalWrite(PIN_LED,LOW);
    delay(200);
  }
}

void loop()
{
  if (Serial.available() > 0) {
    char c = Serial.read();
    readPlaintext();
  }
}

void readPlaintext() {
  delay(500);
  digitalWrite(PIN_BTN,HIGH);
  // digitalWrite(PIN_TOGGLE,LOW);

  // discard synchronisation pulses
  int i = 0;
  for(i = 0;i < 12;i++)
  {
    pulseIn(PIN_PWM_IN,HIGH);
    digitalWrite(PIN_BTN,LOW);
  }

  // digitalWrite(PIN_BTN,LOW);
  bitPosn = 0;
    
  unsigned long pulseA = pulseIn(PIN_PWM_IN,HIGH,20000);
  // digitalWrite(PIN_TOGGLE,toggleMode);
  // toggleMode = 1 - toggleMode;
  while(pulseA != 0 && bitPosn < 128)
  {
    if(pulseA > 500)
    {
      pewpewpew[bitPosn++] = '0';
      // nextByte += (1 << (7 - bitPosn));
    }
    else
    {
      pewpewpew[bitPosn++] = '1';
    }
    pulseA = pulseIn(PIN_PWM_IN,HIGH,2000);
    if(pulseA == 0)
    {
      delay(5);
      pulseA = pulseIn(PIN_PWM_IN,HIGH,10000);
      if(pulseA == 0)
      {
        break;
      }
    }
    // digitalWrite(PIN_TOGGLE,toggleMode);
    // toggleMode = 1 - toggleMode;
  }
  
  // digitalWrite(PIN_BTN,LOW);
  for(i = 0;i < 66;i++)
  {
      Serial.print((char )pewpewpew[i]);
  }
  Serial.println("#");
  // Serial.println();
  return;
}