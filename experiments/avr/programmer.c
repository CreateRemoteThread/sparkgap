#define F_CPU 16000000L
/*
  - avr multitarget driver board
*/

#include <avr/io.h>
#include <stdio.h>
#include <string.h>

#define BAUD 9600 // define baud
#define BAUDRATE ((F_CPU)/(BAUD*16UL)-1) // set baud rate value for UBRR

#define SPI_DDR DDRB
#define CS      PINB2
#define MOSI    PINB3
#define MISO    PINB4
#define SCK     PINB5

#define SPI_SELECT PINB0
#define LED PINB4
#define DATA PINB0
#define RESET PINB2
#define CLOCK PINB1
#define TRIGGER PINC5

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

void SPI_init()
{
	SPI_DDR |= (1 << CS) | (1 << MOSI) | (1 << SCK);
	SPCR = (1 << SPE) | (1 << MSTR);
	
}

void SPI_HiZ()
{
	SPCR &= ~((1 << SPE) | (1 << MSTR));
	SPI_DDR &= ~((1 << CS) | (1 << MOSI) | (1 << SCK));
	PORTD &= ~((1 << CS) | (1 << MOSI) | (1 << SCK));
}

uint8_t SPI_xfer(uint8_t data)
{
	SPDR = data;
	while(!(SPSR & (1 << SPIF)));
	return SPDR;
}

int main()
{
	DDRB |= (1 << SPI_SELECT) | (1 << TRIGGER);
	PORTB |= (1 << SPI_SELECT);
	uart_init();
	FILE mystdio = FDEV_SETUP_STREAM(uart_transmit, uart_receive, _FDEV_SETUP_RW);
	stdout = &mystdio;
	stdin = &mystdio;
	
	int spi_size = 0;
	char spi_buf[128];
	char trigger_buf[128];
	char ret_buf[128];
	
	while(1)
	{
		memset(spi_buf,0,128);
		memset(trigger_buf,0,128);
		char c = fgetc(stdin);
		while(c != '#')
		{
			putchar('?');
			c = fgetc(stdin);
		}
		spi_size = fgetc(stdin);
		int i = 0;
		// # 0xFF 0xAA 0xFF 0x53 #
		// # trig data trig data #
		for(i = 0;i < spi_size;i++)
		{
			trigger_buf[i] = fgetc(stdin);
			spi_buf[i] = fgetc(stdin);
		}
		c = fgetc(stdin);
		if(c != '#')
		{
			// checksum char.
			putchar('?');
			continue;
		}
		else
		{
			SPI_init();
			putchar('#');
			PORTB &= ~(1 << SPI_SELECT);
			for(i = 0;i < spi_size;i++)
			{
				if(trigger_buf[i] == 0xFF)
				{
					PORTB |= (1 << TRIGGER);
				}
				else
				{
					PORTB &= ~(1 << TRIGGER);
				}
				ret_buf[i] = SPI_xfer(spi_buf[i]);
			}
			PORTB |= (1 << SPI_SELECT);
			SPI_HiZ();
			for(i = 0;i < spi_size;i++)
			{
				putchar(ret_buf[i]);
			}
		}
		/*
		SPI_DDR &= ~(1 << SS);
		x = SPI_masterTransmit(0x55);
		SPI_DDR |= (1 << SS);
		*/
	}
	

	
	putchar('#');
	return 0;
}

