#include <stdio.h>
#include <stdlib.h>

int main(int argc ,char **argv)
{
  unsigned long x = 0;
  unsigned long y = 0;
  unsigned long z = 0;
  int i = 0;
  while(1)
  {
    i = 1 - i;
    z = 0;
    for(x = 0;x < 7500;x++)
    {
      for(y = 0;y < 7500;y++)
      {
        z += 1;
      }  
    }
    printf("%d:%u\n",i,z);
    if(z != 56250000)
    {
      FILE *f = fopen("/data/local/tmp/fuck","w");
      fprintf(f,"%u",z);
      fclose(f);
      exit(0);
    }
  }
}
