
#include <EEPROM.h>
#include <avr/pgmspace.h>

// from : http://lmpautomation.com/blog/?p=63

//###########################################################################################
//HCS301 Keeloq definitions
//###########################################################################################
//#define KEY_METHOD 0              // MUST BE 1 IF NORMAL KEY GEN METHOD TO BE USED
                                  // MUST BE 0 IF SIMPLE KEY GEN METHOD TO BE USED
                                  // (ENCRYPTION KEY= MANUFACTURER KEY)
// Key Method is currently selected from HMI Menu!                                  
                                  
#define HCS30X 1                  // MUST BE 1 IF PROGRAMMING HCS300-301,
                                  // MUST BE 0 IF PROGRAMMING HCS200
// MCODE: 0123456789ABCDEF    //Defined on LCD HMI 
//#define MCODE_0 0x0123            // LSWORD    
//#define MCODE_1 0x4567
//#define MCODE_2 0x89AB
//#define MCODE_3 0xCDEF            // MSWORD
#define SYNC 0X0000               // SYNCRONOUS COUNTER
//#define SEED_0 0x0000             // 2 WORD SEED VALUE   //Defined on LCD HMI
//#define SEED_1 0x0000
//#define SER_0 0x4567              // Serial Number LSB     //Defined on LCD HMI  
//#define SER_1 0x0123              // Serial Number MSB (MSbit will set 1 for Auto Shut off function) 
#define ENV_KEY 0x0000            // ENVELOPE KEY (NOT USED FOR HCS200)
#define AUTOFF 1                  // AUTO SHUT OFF TIMER ( NOT USED FOR HCS200)
//#define DISC70 0x00               // DISCRIMINATION BIT7-BIT0 Should be equal to 10 LSB of SN
//#define DISC8 0                   // DISCRIMINATION BIT8
//#define DISC9 0                   // DISCRIMINATION BIT9
#define DISC70 (SER_0 & 0x00FF)
#define DISC8 ((SER_0 & 0x0100)>>8)
#define DISC9 ((SER_0 & 0x0200)>>9)
#define OVR0 0                    // OVERFLOW BIT0 (DISC10 for HCS200)
#define OVR1 0                    // OVERFLOW BIT1(DISC11 for HCS200)
#define VLOW 1                    // LOW VOLTAGE TRIP POINT SELECT BIT (1=High voltage)
#define BSL0 0                    // BAUD RATE SELECT BIT0
#define BSL1 0                    // BAUD RATE SELECT BIT1(RESERVED for HCS200)
#define EENC 0                    // ENVELOPE ENCRYPTION SELECT(RESERVED for
                                  // HCS200)
#define DISEQSN 1                 // IF DISEQSN=1 SET DISCRIMINANT EQUAL TO
                                  // SERNUM BIT10-0 IF DISEQSN=0 SET DISCRIMINANT
                                  // AS defineD ABOVE

#define NUM_WRD 12                // NUMBER OF WORD TO PROGRAM INTO HCS
#define RES 0X0000                // RESERVED WORD
#define CONF_HI ((EENC<<7)|(BSL1<<6)|(BSL1<<5)|(VLOW<<4)|(OVR1<<3)|(OVR0<<2)|(DISC9<<1)|DISC8)
                                  
#define CLK 8               //(OUT PIN) Clock (S2) for Programming HCS //// White Wire
#define DATA 9              // (IN/OUT PIN) Data (PWM) for Programming HCS   //Blue Wire
#define HCSVDD 10            // (OUT PIN) HCS Vdd line      //Red Wire

// ****** HCS TIME PROGRAMMING EQUATE ********
#define Tps 4          // PROGRAM MODE SETUP TIME 4mS (3,5mS min, 4,5 max)
#define Tph1 4          // HOLD TIME 1 4mS (3,5mS min)
#define Tph2 62          // HOLD TIME 2 62uS (50uS min)
#define Tpbw 3          // BULK WRITE TIME 3mS (2,2mS min)
#define Tclkh 35          // CLOCK HIGH TIME 35uS (25uS min)
#define Tclkl 35          // CLOCK LOW TIME 35uS (25uS min)
#define Twc 40          // PROGRAM CYCLE TIME 40mS (36mS min)
word MCODE_0 = 0xCDEF;            // LSWORD    
word MCODE_1 = 0x89AB;
word MCODE_2 = 0x4567;
word MCODE_3 = 0x0123;            // MSWORD
word SEED_0 = 0x0000;             // 2 WORD SEED VALUE
word SEED_1 = 0x0000;
word SER_0 = 0x4567;              // Serial Number LSB
word SER_1 = 0x0123;              // Serial Number MSB (MSbit will set 1 for Auto Shut off function) 
boolean KEY_METHOD = 0;
word SER_0_Temp;                //Temp Serial Number copy for HMI Information
word SER_1_Temp;                //Temp Serial Number copy for HMI Information

//###########################################################################################
//PROCESS VARIABLES
//###########################################################################################
byte HMI_Number = 1; //Defines the HMI Number
byte Previous_HMI_Number = 0; //Defines the Previous HMI Number
byte Process_State = 1; //Defines the Process State Number
byte Previous_Process_State = 1; //Defines the Previous Process State Number

//###########################################################################################
//INTERFACE VARIABLES
//###########################################################################################
unsigned long LastTime = 0;
unsigned long DisplayLastTime = 0;
unsigned long DisplayRate = 400;
unsigned long CalculationsLastTime = 0;
unsigned long CalculationsRate = 1000;
unsigned long AnalogReadLastTime = 0;
unsigned long AnalogReadRate = 2;
unsigned long AnalogClearLastTime = 0;
unsigned long AnalogClearRate = 20;
signed int LCD_Cursor_Position = 0;
int LCD_Buttons_RAW = 0;
const int  ADC_key_value[5] ={30, 150, 360, 535, 760 }; // SEL<30 ->0; R<150 ->1; DN<360 ->2; UP<535 ->3; L<760 ->4
int NUM_KEYS = 5;
int Key_Value=100;
int Oldkey=100;
const int LCD_BUTTONS_PIN = A0;  // Analog input pin that the LCD_Buttons are connected  


//###########################################################################################
//SYSTEM VARIABLES
//###########################################################################################
char TempStringWord[5];
char TempStringDoubleByte[16];
word TempWord;
word Key[4];
word EEPROM_Write_Buffer[12];
word EEPROM_Read_Buffer[12];
boolean EEPROM_Write_Error = false;
boolean Button_State = false;


int i=0;

//#############################################################################
//  SETUP FUNCTION
//#############################################################################
void setup()
{
  Serial.begin(115200);
  pinMode(DATA, OUTPUT);      
  pinMode(CLK, OUTPUT);   
  pinMode(HCSVDD, OUTPUT);  
  // pinMode(PROG, INPUT_PULLUP);  //Energia: pinMode(PROG, INPUT_PULLUP);
  digitalWrite(DATA, LOW);
  digitalWrite(CLK, LOW);
  digitalWrite(HCSVDD, LOW);
  Serial.println("test");
}

//#############################################################################
//  MAIN LOOP
//#############################################################################
void loop()
{
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'p')
    {
      Serial.write("Programming!\n");
      ProgrammSimple();
    }
  }
}

void ProgrammSimple() {
   int i=0;
   Key[i] = 0x1122;  i++;
   Key[i] = 0x3344;  i++;
   Key[i] = 0x5566;  i++;
   Key[i] = 0x7788;  i++;  
  
  Serial.println("Encryption Key: ");
  for(int i=3; i>=0; i--){
    sprintf(TempStringWord, "%.4X", Key[i]);
    Serial.print(TempStringWord);
  }
  Serial.println("");
  delay(100);
  //lcd.print("...");
  //Prepare EEPROM_Write_Buffer to write
  EEPROM_Write_Buffer[0]=Key[0];
  EEPROM_Write_Buffer[1]=Key[1];
  EEPROM_Write_Buffer[2]=Key[2];
  EEPROM_Write_Buffer[3]=Key[3];
  EEPROM_Write_Buffer[4]=SYNC;
  EEPROM_Write_Buffer[5]=0x0000;
  EEPROM_Write_Buffer[6]=SER_0;  //Serial Number Low Word
  EEPROM_Write_Buffer[7]=(SER_1 | (AUTOFF<<15));  //Serial Number High Byte + SET THE AUTO SHUT-OFF TIMER
  EEPROM_Write_Buffer[8]=SEED_0;
  EEPROM_Write_Buffer[9]=SEED_1;
  EEPROM_Write_Buffer[10]=ENV_KEY;
  EEPROM_Write_Buffer[11]=((CONF_HI<<8)|DISC70);
  delay(100);

  //START M_PROG_INIT
  digitalWrite(DATA, LOW);
  digitalWrite(CLK, LOW);
  digitalWrite(HCSVDD, HIGH);
  delay(16); //delay 16milis
  //M_PROG_SETUP
  digitalWrite(CLK, HIGH);
  delay(Tps); //WAIT Program mode Setup Time (Tps)
  digitalWrite(DATA, HIGH);
  delay(Tph1);  //WAIT Program Hold Time 1 (Tph1)
  digitalWrite(DATA, LOW);
  delayMicroseconds(Tph2);     //WAIT Program Hold Time 2 (Tph2)
  //M_PROG_BULK_ER
  digitalWrite(CLK, LOW);
  delay(Tpbw);     //WAIT Program Bulk Write Time (Tpbw)
  
  Serial.println("Writting EEPROM...");
  
  for(int i=0; i<12; i++) { //One word at time
    for(int j=0; j<16; j++) {  //One bit at time
      digitalWrite(CLK, HIGH);
      if ( bitRead(EEPROM_Write_Buffer[i],j) ) { //Read bit from word
          digitalWrite(DATA, HIGH);
        } else {
          digitalWrite(DATA, LOW);
        }
      delayMicroseconds(Tclkh);   // Tclkh
      digitalWrite(CLK, LOW);
      delayMicroseconds(Tclkl);   // Tclkl
    } // One bit at time   
    digitalWrite(DATA, LOW);  //END OUTPUT WORD  DATA=0
    delay(Twc); //WAIT FOR WORD Write Cycle Time (Twc)
  } //One word at time
  //desligar linhas!
  Serial.println("Writting EEPROM Complete!");
  pinMode(DATA, INPUT);
  delay(100);
}
 
boolean Verify_EEPROM()  { 
  Serial.println("Reading EEPROM...");
  // lcd.setCursor(1,1);

  for(int i=0; i<12; i++) { //One word at time
    EEPROM_Read_Buffer[i]=0xFFFF;  //Fill buffer with 0xFF
    for(int j=0; j<16; j++) {  //One bit at time
      delay(Twc); //WAIT FOR WORD Write Cycle Time (Twc)
      if(digitalRead(DATA)) {
        bitSet(EEPROM_Read_Buffer[i],j);
      }
      else {
        bitClear(EEPROM_Read_Buffer[i],j);        
      }
      digitalWrite(CLK, HIGH);
      delayMicroseconds(Tclkh);   // Tclkh
      digitalWrite(CLK, LOW);
      delayMicroseconds(Tclkl);   // Tclkl
    } // One bit at time   
  } //One word at time
  digitalWrite(HCSVDD, LOW); digitalWrite(CLK, LOW);     
}
