#include <stdint.h>

#define F_CPU 16000000UL
#define _SFR_(mem_addr)     (*(volatile uint8_t *)(0x5000 + (mem_addr)))

#define PB_ODR      _SFR_(0x05)
#define PB_DDR      _SFR_(0x07)
#define PB_CR1      _SFR_(0x08)
#define PB_CONFIRM 6

#define PC_ODR      _SFR_(0x0A)
#define PC_DDR      _SFR_(0x0C)
#define PC_CR1      _SFR_(0x0D)
#define LED_PIN 2
#define LED_CONFIRM 0

static inline void delay_ms(uint16_t ms) {
    uint32_t i;
    for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
        __asm__("nop");
}

// PIN_LED goes on to confirm the counting loop
// PIN_CONFIRM is pulled high as trigger, and pulled low to confirm aliveness
// glitch is when PIN_CONFIRM = 1 and PIN_LED = 0

void main() 
{
    PB_DDR |= (1 << PB_CONFIRM);
    PB_CR1 |= (1 << PB_CONFIRM);
    PC_DDR |= (1 << LED_PIN) | (1 << LED_CONFIRM); // configure PD4 as output
    PC_CR1 |= (1 << LED_PIN) | (1 << LED_CONFIRM); // push-pull mode
    uint32_t x;
    uint32_t y;
    uint32_t z;
    while(1)
    {
      PB_ODR |= (1 << PB_CONFIRM);
      z = 0;
      for(x =0;x < 200;x++)
      {
        for(y = 0;y < 200;y++)
        {
          z += 1;
        }
      }
      if(z == 40000)
      {
        PC_ODR ^= (1 << LED_PIN);
      }
      PB_ODR &= ~(1 << PB_CONFIRM);
      while(1)
      {
      }
    }
}
