/**
  @Generated PIC24 / dsPIC33 / PIC32MM MCUs Source File

  @Company:
    Microchip Technology Inc.

  @File Name:
    mcc.c

  @Summary:
    This is the mcc.c file generated using PIC24 / dsPIC33 / PIC32MM MCUs

  @Description:
    This header file provides implementations for driver APIs for all modules selected in the GUI.
    Generation Information :
        Product Revision  :  PIC24 / dsPIC33 / PIC32MM MCUs - pic24-dspic-pic32mm : 1.55
        Device            :  PIC24FJ64GB002
    The generated drivers are tested against the following:
        Compiler          :  XC16 v1.34
        MPLAB             :  MPLAB X v4.15
*/

/*
    (c) 2016 Microchip Technology Inc. and its subsidiaries. You may use this
    software and any derivatives exclusively with Microchip products.

    THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
    EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
    WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
    PARTICULAR PURPOSE, OR ITS INTERACTION WITH MICROCHIP PRODUCTS, COMBINATION
    WITH ANY OTHER PRODUCTS, OR USE IN ANY APPLICATION.

    IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
    WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
    BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
    FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
    ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
    THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.

    MICROCHIP PROVIDES THIS SOFTWARE CONDITIONALLY UPON YOUR ACCEPTANCE OF THESE
    TERMS.
*/

// Configuration bits: selected in the GUI

// CONFIG4
#pragma config DSWDTPS = DSWDTPSF    // DSWDT Postscale Select->1:2,147,483,648 (25.7 days)
#pragma config DSWDTOSC = LPRC    // Deep Sleep Watchdog Timer Oscillator Select->DSWDT uses Low Power RC Oscillator (LPRC)
#pragma config RTCOSC = SOSC    // RTCC Reference Oscillator  Select->RTCC uses Secondary Oscillator (SOSC)
#pragma config DSBOREN = ON    // Deep Sleep BOR Enable bit->BOR enabled in Deep Sleep
#pragma config DSWDTEN = ON    // Deep Sleep Watchdog Timer->DSWDT enabled

// CONFIG3
#pragma config WPFP = WPFP63    // Write Protection Flash Page Segment Boundary->Highest Page (same as page 42)
#pragma config SOSCSEL = IO    // Secondary Oscillator Pin Mode Select->SOSC pins have digital I/O functions (RA4, RB4)
#pragma config WUTSEL = LEG    // Voltage Regulator Wake-up Time Select->Default regulator start-up time used
#pragma config WPDIS = WPDIS    // Segment Write Protection Disable->Segmented code protection disabled
#pragma config WPCFG = WPCFGDIS    // Write Protect Configuration Page Select->Last page and Flash Configuration words are unprotected
#pragma config WPEND = WPENDMEM    // Segment Write Protection End Page Select->Write Protect from WPFP to the last page of memory

// CONFIG2
#pragma config POSCMOD = HS    // Primary Oscillator Select->HS Oscillator mode selected
#pragma config I2C1SEL = PRI    // I2C1 Pin Select bit->Use default SCL1/SDA1 pins for I2C1 
#pragma config IOL1WAY = ON    // IOLOCK One-Way Set Enable->Once set, the IOLOCK bit cannot be cleared
#pragma config OSCIOFNC = ON    // OSCO Pin Configuration->OSCO pin functions as port I/O (RA3)
#pragma config FCKSM = CSECME    // Clock Switching and Fail-Safe Clock Monitor->Sw Enabled, Mon Enabled
#pragma config FNOSC = PRI    // Initial Oscillator Select->Primary Oscillator (XT, HS, EC)
#pragma config PLL96MHZ = ON    // 96MHz PLL Startup Select->96 MHz PLL Startup is enabled automatically on start-up
#pragma config PLLDIV = DIV2    // USB 96 MHz PLL Prescaler Select->Oscillator input divided by 2 (8 MHz input)
#pragma config IESO = ON    // Internal External Switchover->IESO mode (Two-Speed Start-up) enabled

// CONFIG1
#pragma config WDTPS = PS32768    // Watchdog Timer Postscaler->1:32768
#pragma config FWPSA = PR128    // WDT Prescaler->Prescaler ratio of 1:128
#pragma config WINDIS = OFF    // Windowed WDT->Standard Watchdog Timer enabled,(Windowed-mode is disabled)
#pragma config FWDTEN = ON    // Watchdog Timer->Watchdog Timer is enabled
#pragma config ICS = PGx1    // Emulator Pin Placement Select bits->Emulator functions are shared with PGEC1/PGED1
#pragma config GWRP = OFF    // General Segment Write Protect->Writes to program memory are allowed
#pragma config GCP = OFF    // General Segment Code Protect->Code protection is disabled
#pragma config JTAGEN = OFF    // JTAG Port Enable->JTAG port is disabled

#include "mcc.h"

void SYSTEM_Initialize(void)
{
    PIN_MANAGER_Initialize();
    OSCILLATOR_Initialize();
    INTERRUPT_Initialize();
    UART1_Initialize();
}

void OSCILLATOR_Initialize(void)
{
    // CPDIV 1:1; PLLEN disabled; RCDIV FRC/1; DOZE 1:8; DOZEN disabled; ROI disabled; 
    CLKDIV = 0x3000;
    // TUN Center frequency; 
    OSCTUN = 0x0000;
    // ROEN disabled; ROSEL disabled; RODIV Base clock value; ROSSLP disabled; 
    REFOCON = 0x0000;
    // CF no clock failure; NOSC PRI; SOSCEN disabled; POSCEN disabled; CLKLOCK unlocked; OSWEN Switch is Complete; IOLOCK not-active; 
    __builtin_write_OSCCONH((uint8_t) ((0x0200 >> _OSCCON_NOSC_POSITION) & 0x00FF));
    __builtin_write_OSCCONL((uint8_t) (0x0200 & 0x00FF));
}

/**
 End of File
*/