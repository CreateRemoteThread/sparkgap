/*! \file max3421.c
  \author Travis Goodspeed
  \brief SPI Driver for MAX342x USB Controllers
*/


#include "command.h"

#ifdef __MSPGCC__
#include <msp430.h>
#else
#include <signal.h>
#include <msp430.h>
#include <iomacros.h>
#endif

#include "maxusb.h"

#define MAXUSBAPPLICATION

#include "platform.h"


#define SETTRIG P5OUT|=BIT5
#define CLRTRIG P5OUT&=~BIT5

#define SET2N7000 P5OUT|=BIT4
#define CLR2N7000 P5OUT&=~BIT4


// define for the app list.
app_t const maxusb_app = {
	/* app number */
	MAXUSB,

	/* handle fn */
	maxusb_handle_fn,

	/* name */
	"MAXUSB",

	/* desc */
	"\tThis allows you to write USB Host or USB Device drivers for\n"
	"\t the MAX3421 and MAX3420 chips.\n"
};

//! Set up the pins for SPI mode.
void maxusb_setup(){
  SETSS;
  SPIDIR|=MOSI+SCK+BIT0; //BIT0 might be SS
  SPIDIR&=~MISO;
  P4DIR&=~TST; //TST line becomes interrupt input.
  P4DIR&=~BIT7; //GPX pin.
  P2DIR|=RST;
  DIRSS;

  // gpio trigger. 
  P5DIR|=BIT5;
  P5DIR|=BIT4;
  CLRTRIG;
  CLR2N7000;
  
  //Setup the configuration pins.
  //This might need some delays.
  CLRRST; //Put the chip into RESET.
  SETSS;  //Deselect the chip, end any existing transation.
  SETRST; //Bring the chip out of RESET.
}



//! Handles a MAXUSB monitor command.
void maxusb_handle_fn( uint8_t const app,
		       uint8_t const verb,
		       uint32_t const len){
  unsigned long i;

  //Raise !SS to end transaction, just in case we forgot.
  SETSS;

  switch(verb){
  case READ:
  case WRITE:
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;

  /*
    overriden: set glitch trigger to give
    a stable start point for cwlite.
  */
  case PEEK:
    SETTRIG;
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    CLRTRIG;
    break;

  /*
   * overridden: manually control the 
   */
  case POKE://TODO poke a register.
    if(len == 0)
    {
	    CLR2N7000;
    }
    else
    {
	    if(cmddata[0] == 0)
	    {
		    CLR2N7000;
	    }
	    else
	    {
		    SET2N7000;
	    }
    }
    txdata(app,verb,1);
    break;
    
  case SETUP:
    maxusb_setup();
    txdata(app,verb,0);
    break;
  }
	
  //Raise !SS to end transaction, in case we forgot.
  SETSS;
}
