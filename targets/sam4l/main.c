/**
 * \file
 *
 * \brief Empty user application template
 *
 */

/**
 * \mainpage User Application template doxygen documentation
 *
 * \par Empty user application template
 *
 * Bare minimum empty user application template
 *
 * \par Content
 *
 * -# Include the ASF header files (through asf.h)
 * -# "Insert system clock initialization code here" comment
 * -# Minimal main function that starts with a call to board_init()
 * -# "Insert application code here" comment
 *
 */

/*
 * Include header files for all drivers that have been imported from
 * Atmel Software Framework (ASF).
 */
/*
 * Support and FAQ: visit <a href="https://www.microchip.com/support/">Microchip Support</a>
 */

#define CONF_UART USART0
#include <asf.h>
#include <stdio.h>

usart_serial_options_t  uart_serial_options = {
	.baudrate = 115200,
	.charlength = US_MR_CHRL_8_BIT,
	.paritytype = US_MR_PAR_NO,
	.stopbits = US_MR_NBSTOP_1_BIT,
};

#define ioport_set_pin_peripheral_mode(pin, mode) \
do {\
	ioport_set_pin_mode(pin, mode);\
	ioport_disable_pin(pin);\
} while (0)

int main (void)
{
	sysclk_init();
	ioport_init();
	board_init();
	char c;
	
	ioport_pin_t pin_tx = IOPORT_CREATE_PIN(IOPORT_GPIOA,12);
	ioport_pin_t pin_rx = IOPORT_CREATE_PIN(IOPORT_GPIOA,11);
	ioport_pin_t pin_led = IOPORT_CREATE_PIN(IOPORT_GPIOA,4);
	
	ioport_set_pin_peripheral_mode(pin_rx, MUX_PA11A_USART0_RXD);
	ioport_set_pin_peripheral_mode(pin_tx, MUX_PA12A_USART0_TXD);
	
	usart_serial_init(CONF_UART,&uart_serial_options);
	
	ioport_set_pin_dir(pin_led,IOPORT_DIR_OUTPUT);
	ioport_set_pin_level(pin_led,true);
	
	usart_serial_putchar(CONF_UART,'1');
	while(1)
	{
		// usart_serial_putchar(CONF_UART,'r');
		usart_serial_read_packet(CONF_UART,&c,1);
		usart_serial_putchar(CONF_UART,c);
	}
}

