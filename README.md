# embedded-peripheral-config-generator
YAML based embedded peripheral configuration parser

this python tool parses a YAML file describing peripherals (GPIO, UART, I2C, timers) and generates STM32 HAL C code to initialize them.

## Features

- define peripherals using an easy YAML format. 
- validate your config for mistakes.  
- generate init code for GPIO pins, UART, I2C, and timers. 
- supports setting GPIO alternate function macros directly in YAML.  

## How to Use

### 1. Create and activate a Python virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# or
venv\Scripts\activate             # Windows
```

### 2. Install dependencies

```bash
pip install pyyaml
```

### 3. Prepare your YAML peripheral configuration file

Example `peripheral_config.yaml` snippet for UART and GPIO:

```yaml
gpio:
  pins:
    - pin: "PA9"
      direction: "output"
      pull: "none"
      speed: "high"
      alt_function: GPIO_AF7_USART1
      comment: "UART1 TX"

communication:
  uart:
    - instance: "USART1"
      enabled: true
      baudrate: 115200
```

### 4. Run the parser to validate config and generate code

```bash
python3 peripheral_parser.py peripheral_config.yaml --output peripheral_init.c
```

### 5. Print a summary of your config without generating code

```bash
python3 peripheral_parser.py peripheral_config.yaml --summary
```

### 6. Validate config only, no code generation

```bash
python3 peripheral_parser.py peripheral_config.yaml --validate-only
```

## Notes

- the tool focuses on setup code for pins and peripherals, not device-specific sensor drivers.    
- support error checking and validation.
- support comments or defaults.

## Why YAML?

- YAML is popular in embedded ecosystems (ex:- Zephyr, CubeMX, and many hardware abstraction projects) for its readability and support for structured, hierarchical descriptions.
- clear and human-friendly configuration format.  
- supports structured data and comments. 
- easy to extend and maintain.

Feel free to customize and extend the parser as needed. This tool streamlines embedded peripheral bring-up and save you time!