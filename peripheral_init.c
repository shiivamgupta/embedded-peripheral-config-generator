/* auto-generated for STM32F4-Discovery */
#include "stm32f4xx_hal.h"

static void init_gpio(void) {
    GPIO_InitTypeDef GpioStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    /* PA0: on-board user button (B1) input */
    GpioStruct.Pin = GPIO_PIN_0;
    GpioStruct.Mode = GPIO_MODE_INPUT;
    GpioStruct.Pull = GPIO_PULLUP;
    GpioStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;
    HAL_GPIO_Init(GPIOA, &GpioStruct);

    __HAL_RCC_GPIOD_CLK_ENABLE();
    /* PD12: on-board green user LED (LD4) */
    GpioStruct.Pin = GPIO_PIN_12;
    GpioStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GpioStruct.Pull = GPIO_NOPULL;
    GpioStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;
    HAL_GPIO_Init(GPIOD, &GpioStruct);

    /* PA9: debug console TX */
    GpioStruct.Pin = GPIO_PIN_9;
    GpioStruct.Mode = GPIO_MODE_AF_PP;
    GpioStruct.Alternate = GPIO_AF7_USART1;
    GpioStruct.Pull = GPIO_NOPULL;
    GpioStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GpioStruct);

    /* PA10: debug console RX */
    GpioStruct.Pin = GPIO_PIN_10;
    GpioStruct.Mode = GPIO_MODE_AF_PP;
    GpioStruct.Alternate = GPIO_AF7_USART1;
    GpioStruct.Pull = GPIO_PULLUP;
    GpioStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GpioStruct);

    __HAL_RCC_GPIOB_CLK_ENABLE();
    /* PB6: i2c bus clock */
    GpioStruct.Pin = GPIO_PIN_6;
    GpioStruct.Mode = GPIO_MODE_AF_PP;
    GpioStruct.Alternate = GPIO_AF4_I2C1;
    GpioStruct.Pull = GPIO_NOPULL;
    GpioStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;
    HAL_GPIO_Init(GPIOB, &GpioStruct);

    /* PB7: i2c bus data */
    GpioStruct.Pin = GPIO_PIN_7;
    GpioStruct.Mode = GPIO_MODE_AF_PP;
    GpioStruct.Alternate = GPIO_AF4_I2C1;
    GpioStruct.Pull = GPIO_NOPULL;
    GpioStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;
    HAL_GPIO_Init(GPIOB, &GpioStruct);

}

UART_HandleTypeDef huart1;
void init_USART1(void) {
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&huart1) != HAL_OK) {
        Error_Handler();
    }
}

I2C_HandleTypeDef hi2c1;
void init_I2C1(void) {
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2 = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}

TIM_HandleTypeDef htim2;
void init_TIM2(void) {
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 83999;
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 999;
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    if (HAL_TIM_Base_Init(&htim2) != HAL_OK) {
        Error_Handler();
    }
}

TIM_HandleTypeDef htim3;
void init_TIM3(void) {
    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 167;
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 999;
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    if (HAL_TIM_Base_Init(&htim3) != HAL_OK) {
        Error_Handler();
    }
}

void initialize_peripherals(void) {
    init_gpio();
    init_USART1();
    init_I2C1();
    init_TIM2();
    init_TIM3();
}
