/**
	sam4l aes sample (with hardware countermeasure)
 */

#define CONF_UART USART0
#include <asf.h>
#include <stdio.h>
#include "hal_serial.h"
#include "aes.h"

char aes_data[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
char aes_key[16] = {0x12,0x34,0x56,0x78,0x9a,0xbc,0xde,0xf0,0x12,0x34,0x56,0x78,0x9a,0xbc,0xde,0xf0};
char aes_out[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

char cmd[64];

// AES_init_ctx(&ctx, aes_key);

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
	
		struct AES_ctx ctx;
	
	GpioPort *base = arch_ioport_port_to_base(IOPORT_GPIOA);
	
	ioport_pin_t pin_tx = IOPORT_CREATE_PIN(IOPORT_GPIOA,12);
	ioport_pin_t pin_rx = IOPORT_CREATE_PIN(IOPORT_GPIOA,11);
	ioport_pin_t pin_led = IOPORT_CREATE_PIN(IOPORT_GPIOA,4);
	
	ioport_set_pin_peripheral_mode(pin_rx, MUX_PA11A_USART0_RXD);
	ioport_set_pin_peripheral_mode(pin_tx, MUX_PA12A_USART0_TXD);
	
	usart_serial_init(CONF_UART,&uart_serial_options);
	
	ioport_set_pin_dir(pin_led,IOPORT_DIR_OUTPUT);
	/*
	base->GPIO_OVRS = 1 << 4;
	base->GPIO_OVRC = 1 << 4;
	*/

	int i = 0;
	hal_puts("hello\r\n");
	while(1)
	{
		for(i = 0;i < 64;i++)
		{
			cmd[i] = '\x00';
		}
		hal_getline(cmd);
		if(cmd[0] == 'e')
		{
			// encrypt
			for(i = 0;i < 16;i++)
			{
				aes_data[i] = hal_hex2bin((char *)(cmd + 1 + i * 2));
			}
			AES_init_ctx(&ctx, aes_key);
			base->GPIO_OVRS = 1 << 4;
			AES_ECB_encrypt(&ctx, aes_data);
			base->GPIO_OVRC = 1 << 4;
			for(i = 0;i < 16;i++)
			{
				hal_bin2hex(aes_data[i]);
			}
			hal_puts("\r\n");
		}
		else if(cmd[0] == 'k')
		{
			// rekey
			for(i = 0;i < 16;i++)
			{
				aes_key[i] = hal_hex2bin((char *)(cmd + 1 + i * 2));
			}
			for(i = 0;i < 16;i++)
			{
				hal_bin2hex(aes_key[i]);
			}
			hal_puts("\r\n");
		}
		else
		{
			hal_puts("err: unknown command\r\n");
		}
	}
}

