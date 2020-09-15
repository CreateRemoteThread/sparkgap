#include <stdint.h>

// 0xAA is the Read Protection. SWIM will be unable to connect.

#define F_CPU 2000000UL
#define _SFR_(mem_addr)     (*(volatile uint8_t *)(0x5000 + (mem_addr)))

#define PD_ODR      _SFR_(0x0F)
#define PD_DDR      _SFR_(0x11)
#define PD_CR1      _SFR_(0x12)
#define LED_PIN     0

static inline void delay_ms(uint16_t ms) {
    uint32_t i;
    for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
        __asm__("nop");
}
void main() 
{
    PD_DDR |= (1 << LED_PIN); // configure PD4 as output
    PD_CR1 |= (1 << LED_PIN); // push-pull mode
    uint32_t x;
    uint32_t y;
    uint32_t z;
    while (1) 
    {
      z = 0;
      for(x = 0;x < 250;x++)
      {
          for(y = 0;y < 250;y++)
          {
            z++;
          }
      }
      if(z == 62500)
      {
        PD_ODR ^= (1 << LED_PIN);
      }
      // delay_ms(250);
    }
}
