
#include <stdio.h>
#include "main.h"
#include "ecdh.h"

#define TRIGGER_ON HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,1)
#define TRIGGER_OFF HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,0)

UART_HandleTypeDef huart1;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);

void stm_gets(char *p)
{
	char r = 0;
	char wHead = 0;
	while(r != 0x0d && r != 0x0a)
	{
		HAL_UART_Receive(&huart1,&r,1,HAL_MAX_DELAY);
		p[wHead++] = r;
	}
	p[wHead] = 0;
	return;
}

typedef struct
{
  uint32_t a;
  uint32_t b;
  uint32_t c;
  uint32_t d;
} prng_t;

static prng_t prng_ctx;

static uint32_t prng_rotate(uint32_t x, uint32_t k)
{
  return (x << k) | (x >> (32 - k));
}

static uint32_t prng_next(void)
{
  uint32_t e = prng_ctx.a - prng_rotate(prng_ctx.b, 27);
  prng_ctx.a = prng_ctx.b ^ prng_rotate(prng_ctx.c, 17);
  prng_ctx.b = prng_ctx.c + prng_ctx.d;
  prng_ctx.c = prng_ctx.d + e;
  prng_ctx.d = e + prng_ctx.a;
  return prng_ctx.d;
}

static void prng_init(uint32_t seed)
{
  uint32_t i;
  prng_ctx.a = 0xf1ea5555;
  prng_ctx.b = prng_ctx.c = prng_ctx.d = seed;

  for (i = 0; i < 31; ++i)
  {
    (void) prng_next();
  }
}

int main(void)
{
  static uint8_t puba[ECC_PUB_KEY_SIZE];
  static uint8_t prva[ECC_PRV_KEY_SIZE];
  static uint8_t seca[ECC_PUB_KEY_SIZE];
  static uint8_t pubb[ECC_PUB_KEY_SIZE];
  static uint8_t prvb[ECC_PRV_KEY_SIZE];
  static uint8_t secb[ECC_PUB_KEY_SIZE];
  uint32_t i;
  char cmd[128];

  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_USART1_UART_Init();

  static int initialized = 0;
  if (!initialized)
  {
    prng_init(0xf4d3f4c3 | 0xc4f3b4b3);
    initialized = 1;
  }

  HAL_UART_Transmit(&huart1,"hello\r\n",7,HAL_MAX_DELAY);

  while (1)
  {
	  cmd[0] = 0x00;
	  stm_gets(cmd);
	  if(cmd[0] == 'z')
	  {
		  for (i = 0; i < ECC_PRV_KEY_SIZE; ++i)
		  {
			  prva[i] = 0x01;
		  }
		  // TRIGGER_ON;
		  ecdh_generate_keys(puba, prva);
		  // TRIGGER_OFF;
	  }
	  else if(cmd[0] == 'r')
	  {
		  for (i = 0; i < ECC_PRV_KEY_SIZE; ++i)
		  {
		    prva[i] = prng_next();
		  }
	  	  ecdh_generate_keys(puba, prva);
	  }
	  else if(cmd[0] == 'f')
	  {
		  for (i = 0; i < ECC_PRV_KEY_SIZE; ++i)
		  {
			  prva[i] = 0xFF;
		  }
		  // TRIGGER_ON;
		  ecdh_generate_keys(puba, prva);
		  // TRIGGER_OFF;
	  }
	  else if(cmd[0] == 'a')
	  {
		  for (i = 0; i < ECC_PRV_KEY_SIZE; ++i)
	  	  {
	  		  prva[i] = 0xAA;
	  	  }
		  // TRIGGER_ON;
	  	  ecdh_generate_keys(puba, prva);
	  	  // TRIGGER_OFF;
	  }
	  // ecdh_shared_secret(prva, pubb, seca);
	  HAL_UART_Transmit(&huart1,"done\r\n",6,10);
  }
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 9600;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13 | GPIO_PIN_14;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

