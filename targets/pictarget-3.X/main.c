#include "mcc_generated_files/mcc.h"

#define FCY 8000000ULL
#include <libpic30.h>
#include <string.h>
#include <stdio.h>

#define CBC 1
#define CTR 1
#define ECB 1

#include "aes.h"
#include "rsa.h"
#include "des.h"

DIGIT_T m[MAXDIGITS],out[MAXDIGITS],x,y;

const DIGIT_T     Mod[MAXDIGITS] = { 0x01, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6};
const DIGIT_T PrivExp[MAXDIGITS] = { 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa};
const DIGIT_T PrivExp_ZERO[MAXDIGITS] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

uint8_t key[] = { 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c };
uint8_t in[]  = { 0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96, 0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a };
uint8_t aes_out[]  = { 0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96, 0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a };

void getBuffer(char *buffer, int maxSize)
{
    int i = 0;
    for(;i < maxSize;i++)
    {
        buffer[i] = UART1_Read();
        if(buffer[i] == '\r' || buffer[i] == '\n')
        {
            buffer[i] = '\0';
            return;
        }
    }
}

void putBuffer(char *buffer,int maxSize)
{
    int i = 0;
    for(;i < maxSize;i++)
    {
        if(buffer[i] == '\0')
        {
            return;
        }
        UART1_Write(buffer[i]);
    }
}

void ghetto_puts(char *buffer)
{
    int i = 0;
    int max = strlen(buffer);
    for(;i < max;i++)
    {
        UART1_Write(buffer[i]);
    }
}

int getByteValue(char c)
{
    if(c >= '0' && c <= '9')
    {
        return c - '0';
    }
    else if(c >= 'a' && c <= 'f')
    {
        return c - 'a' + 0x0a;
    }
    else if(c >= 'A' && c <= 'F')
    {
        return c - 'A' + 0x0a;
    }
    else
    {
        return 0;
    }
}

void fetchBytes(char *buf,uint8_t *output)
{

    int i = 0;
    for(;i < 16;i++)
    {
        output[i] = getByteValue(buf[i * 2]) * 0x10 + getByteValue(buf[i * 2 + 1]);
    }

    return;
}

#define DO_RSA 1

int main(void)
{
    SYSTEM_Initialize();
    TRISB &= ~((1 << 7) | (1 << 10));
    PORTB &= ~((1 << 10));
    
    int do_trigger = 1;
    char buf[128];
    
    struct AES_ctx ctx;
    
    int i = 0;

    ghetto_puts("hello\r\n");
    /*
    for(i = 0;i < 3;i++)
    {
        PORTB |= (1 << 7);
        __delay_ms(100);
        PORTB &= ~(1 << 7);
        __delay_ms(50);
    }
     */
        
    
    while (1)
    {
        for(i = 0;i < 128;i++)
        {
            buf[i] = '\0';
        }
        getBuffer(buf,128);
        if(buf[0] == 'k')
        {
            fetchBytes(buf + 1,key);
            UART1_Write('k');
            for(i = 0;i < 16;i++)
            {
                sprintf(buf,"%02x",key[i]);
                ghetto_puts(buf);
            }
            ghetto_puts("\r\n");
        }
        else if(buf[0] == 'e')
        {
            fetchBytes(buf + 1,in);
            AES_init_ctx(&ctx, key);
            if(do_trigger == 1)
            {
                PORTB |= (1 << 10);
                AES_ECB_encrypt(&ctx, in);
                PORTB &= ~(1 << 10);
            }
            else
            {
                AES_ECB_encrypt(&ctx, in);
            }
            UART1_Write('e');
            for(i = 0;i < 16;i++)
            {
                sprintf(buf,"%02x",in[i]);
                ghetto_puts(buf);
            }
            ghetto_puts("\r\n");
        }
        else if(buf[0] == 'R')
        {
            fetchBytes(buf + 1,m);
            if(do_trigger == 1)
            {
                PORTB |= (1 << 10);
                mpModExp(out,m,PrivExp,Mod,MAXDIGITS);
                PORTB &= ~(1 << 10);
            }
            else
            {
                mpModExp(out,m,PrivExp,Mod,MAXDIGITS);
            }
            UART1_Write('e');
            for(i = 0;i < MAXDIGITS;i++)
            {
                sprintf(buf,"%02x",out[i]);
                ghetto_puts(buf);
            }
            ghetto_puts("\r\n");
        }
        else if(buf[0] == 'r')
        {
            fetchBytes(buf + 1,m);
            if(do_trigger == 1)
            {
                PORTB |= (1 << 10);
                mpModExp(out,m,PrivExp_ZERO,Mod,MAXDIGITS);
                PORTB &= ~(1 << 10);
            }
            else
            {
                mpModExp(out,m,PrivExp_ZERO,Mod,MAXDIGITS);
            }
            UART1_Write('e');
            for(i = 0;i < MAXDIGITS;i++)
            {
                sprintf(buf,"%02x",out[i]);
                ghetto_puts(buf);
            }
            ghetto_puts("\r\n");
        }
        else if(buf[0] == 'd')
        {
            fetchBytes(buf + 1,in);
            // PORTB |= (1 << 10);
            des_enc(out, in, key);
            // mpModExp(out,m,PrivExp,Mod,MAXDIGITS);
            // PORTB &= ~(1 << 10);
            UART1_Write('e');
            for(i = 0;i < MAXDIGITS;i++)
            {
                sprintf(buf,"%02x",out[i]);
                ghetto_puts(buf);
            }
            ghetto_puts("\r\n");
        }
        else if(buf[0] == 't')
        {
            do_trigger = 1 - do_trigger;
            if(do_trigger == 1)
            {
                ghetto_puts("triggers on\r\n");
            }
            else
            {
                ghetto_puts("triggers off\r\n");
            }
        }
        else
        {
            ghetto_puts("Unknown instruction\r\n");
        }
        // putBuffer(buf,128);
    }

    return -1;
}
