#define F_CPU 16000000UL

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define CBC 1
#define CTR 1
#define ECB 1

#include "aes.h"
#include "des.h"

#define BAUD 9600 // define baud
#define BAUDRATE ((F_CPU)/(BAUD*16UL)-1) // set baud rate value for UBRR

// function to initialize UART
void uart_init (void)
{
	UBRR0H = (BAUDRATE>>8); // shift the register right by 8 bits
	UBRR0L = BAUDRATE; // set baud rate
	UCSR0B|= (1<<TXEN0)|(1<<RXEN0); // enable receiver and transmitter
	UCSR0C = (3<<UCSZ00);
}

int uart_transmit(char data  )
{
	while (!( UCSR0A & (1<<UDRE0))); // wait while register is free
	UDR0 = data; // load data in the register
	return 0;
}

unsigned char uart_receive( void )
{
	while ( !(UCSR0A & (1<<RXC0)) );
	return UDR0;
}

int main(void)
{
	uart_init();
	FILE mystdio = FDEV_SETUP_STREAM(uart_transmit, uart_receive, _FDEV_SETUP_RW);
	
	stdout = &mystdio;
	stdin = &mystdio;
	
	// fixed 128 bit key... for now.
	uint8_t key[] = { 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c };
	uint8_t in[]  = { 0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96, 0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a };
	uint8_t aes_out[]  = { 0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96, 0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a };
		
	DDRB |= (1 << PORTB1) | (1 << PORTB0);

	struct AES_ctx ctx;
	printf("hello\r");
	char lol[50];
	
	while (1)
	{
		fscanf(stdin,"%s",lol);
		if(lol[0] == 'k')
		{
			char *l = (char *)lol + 1;
			int i = 0;
			for(;i < 16;i++)
			{
				if(l[0] == '\r' || l[0] == '\n')
				{
					break;
				}
				sscanf(l,"%02x",&key[i]);
				l += 2;
			}
			printf("k");
			for(i = 0;i < 16;i++)
			{
				printf("%02x",key[i]);
			}
			printf("\r\n");
		}
		else if(lol[0] == 'e')
		{
			char *l = (char *)lol + 1;
			int i = 0;
			for(;i < 16;i++)
			{
				if(l[0] == '\r' || l[0] == '\n')
				{
					break;
				}
				sscanf(l,"%02x",&in[i]);
				l += 2;
			}
			AES_init_ctx(&ctx, key);
			memcpy(aes_out,in,16);
			PORTB |= (1 << PORTB0);
			AES_ECB_encrypt(&ctx, aes_out);
			PORTB &= ~(1 << PORTB0);
			printf("e");
			for(i = 0;i < 16;i++)
			{
				printf("%02x",aes_out[i]);
			}
			printf("\r\n");
		}
		else if(lol[0] == 'd')
		{
			// only 8 byte DES is implemented, but this is fine.
			char *l = (char *)lol + 1;
			int i = 0;
			for(;i < 8;i++)
			{
				if(l[0] == '\r' || l[0] == '\n')
				{
					break;
				}
				sscanf(l,"%02x",&in[i]);
				l += 2;
			}
			PORTB |= (1 << PORTB0);
			des_enc(aes_out, in, key);
			PORTB &= ~(1 << PORTB0);
			printf("e");
			for(i = 0;i < 8;i++)
			{
				printf("%02x",aes_out[i]);
			}
			printf("\r\n");
		}
		else
		{
			printf("unknown: %s\r\n",lol);
		}
		fflush(stdin);
	}
}
