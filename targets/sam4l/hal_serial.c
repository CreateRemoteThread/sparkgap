#define CONF_UART USART0
#include <asf.h>
#include <stdio.h>
#include "hal_serial.h"

char *hexalpha = "0123456789abcdef";

char hal_nextchar = 0;
char hal_getchar()
{
	usart_serial_getchar(CONF_UART,&hal_nextchar);
	return hal_nextchar;
}

void hal_putchar(char c)
{
	usart_serial_putchar(CONF_UART,c);
}

int hal_getline(char *output)
{
	int i = 0;
	while(true)
	{
		char nc = hal_getchar();
		if(nc == '\n' || nc == '\r' || nc == '\x00')
		{
			output[i] = '\x00';
			break;
		}
		else
		{
			output[i++] = nc;
		}
	}
	return i;
}

void hal_puts(char *input)
{
	int i =0;
	while(input[i] != '\x00')
	{
		hal_putchar(input[i++]);
	}
}

uint8_t nibble2bin(char input)
{
	if(input >= '0' && input <= '9')
	{
		return input - '0';
	}
	else if(input >= 'a' && input <= 'f')
	{
		return input - 'a' + 0xa;
	}
	else if(input >= 'A' && input <= 'F')
	{
		return input - 'A' + 0xa;
	}
}

// 2 bytes only.
uint8_t hal_hex2bin(char *input)
{
	return nibble2bin(input[0]) * 0x10 + nibble2bin(input[1]);
}

void hal_bin2hex(uint8_t input)
{
	hal_putchar(hexalpha[(input >> 4) & 0xF]);
	hal_putchar(hexalpha[input & 0xF]);
}
