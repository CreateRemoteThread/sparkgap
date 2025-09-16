

#ifndef HAL_SERIAL_H_
#define HAL_SERIAL_H_


char hal_getchar();
void hal_putchar(char c);
int hal_getline(char *output);
void hal_puts(char *input);
uint8_t hal_hex2bin(char *input);
void hal_bin2hex(uint8_t data);


#endif /* HAL_SERIAL_H_ */
