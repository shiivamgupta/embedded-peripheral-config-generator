#!/usr/bin/env python3
"""
parse a yaml peripheral config and generate stm32 hal c code for
gpio uart i2c and timers with default value support and comments
"""

import yaml
import argparse
import sys
from pathlib import Path

valid_directions = {"input", "output", "output_open_drain"}
valid_pulls = {"none", "pull_up", "pull_down"}
valid_speeds = {"low", "medium", "high", "very_high"}

pull_map = {
    "none": "GPIO_NOPULL",
    "pull_up": "GPIO_PULLUP",
    "pull_down": "GPIO_PULLDOWN",
}
speed_map = {
    "low": "GPIO_SPEED_FREQ_LOW",
    "medium": "GPIO_SPEED_FREQ_MEDIUM",
    "high": "GPIO_SPEED_FREQ_HIGH",
    "very_high": "GPIO_SPEED_FREQ_VERY_HIGH",
}

# default values for optional parameters
defaults = {
    "gpio": {
        "pull": "none",
        "speed": "medium",
        "direction": "input"
    },
    "uart": {
        "parity": "none",
        "stop_bits": 1,
        "data_bits": 8,
        "enabled": True
    },
    "i2c": {
        "speed": 100000,
        "enabled": True
    },
    "timers": {
        "enabled": True,
        "mode": "timer"
    }
}

def handle_var_name(prefix: str, instance: str):
    lower = instance.lower()
    prefix_map = {
        "usart": "huart",
        "i2c": "hi2c",
        "tim": "htim",
        "timers": "htim",
    }
    for key in prefix_map:
        if lower.startswith(key):
            suffix = lower[len(key):]
            return prefix_map[key] + suffix
    return prefix + lower


class configparser:
    def __init__(self, config_path):
        self.filepath = Path(config_path)
        self.config = {}
        self.errors = []

    def _apply_defaults(self):
        """apply default values to missing optional parameters"""
        # apply gpio defaults
        for pin in self.config.get("gpio", {}).get("pins", []):
            for key, default_val in defaults["gpio"].items():
                if key not in pin:
                    pin[key] = default_val
                    print(f"  applied default {key}='{default_val}' to pin {pin.get('pin', 'unknown')}")

        # apply uart defaults
        for uart in self.config.get("communication", {}).get("uart", []):
            for key, default_val in defaults["uart"].items():
                if key not in uart:
                    uart[key] = default_val
                    print(f"  applied default {key}='{default_val}' to {uart.get('instance', 'uart')}")

        # apply i2c defaults
        for i2c in self.config.get("communication", {}).get("i2c", []):
            for key, default_val in defaults["i2c"].items():
                if key not in i2c:
                    i2c[key] = default_val
                    print(f"  applied default {key}='{default_val}' to {i2c.get('instance', 'i2c')}")

        # apply timer defaults
        for timer in self.config.get("timers", []):
            for key, default_val in defaults["timers"].items():
                if key not in timer:
                    timer[key] = default_val
                    print(f"  applied default {key}='{default_val}' to {timer.get('instance', 'timer')}")

    def load_and_validate(self):
        print(f"loading configuration from {self.filepath}")
        try:
            with self.filepath.open() as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"error config file not found {self.filepath}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"error parsing yaml file details {e}")
            sys.exit(1)

        print("applying default values for missing optional parameters")
        self._apply_defaults()

        self._validate_structure()
        self._validate_board_section()
        self._validate_gpio_section()
        self._validate_communication_section()
        self._validate_timers_section()

        if self.errors:
            print("\nconfiguration validation failed")
            for err in self.errors:
                print(f" - {err}")
            sys.exit(1)

        print("configuration validated successfully")
        return True

    def _validate_structure(self):
        sections = ["board", "gpio", "communication", "timers"]
        for section in sections:
            if section not in self.config:
                self.errors.append(f"missing section {section}")

    def _validate_board_section(self):
        board = self.config.get("board", {})
        for field in ["name", "mcu", "clock_freq"]:
            if field not in board:
                self.errors.append(f"board {field} required")

    def _validate_gpio_section(self):
        pins = self.config.get("gpio", {}).get("pins", [])
        seen = set()
        for idx, pin in enumerate(pins):
            name = pin.get("pin")
            if not name:
                self.errors.append(f"gpio {idx} missing pin")
                continue
            if name in seen:
                self.errors.append(f"duplicate pin {name}")
            seen.add(name)
            if pin.get("direction") not in valid_directions:
                self.errors.append(f"{name} direction must be one of {valid_directions}")
            if pin.get("pull") not in valid_pulls:
                self.errors.append(f"{name} pull must be one of {valid_pulls}")
            if pin.get("speed") not in valid_speeds:
                self.errors.append(f"{name} speed must be one of {valid_speeds}")
            af = pin.get("alt_function")
            if af is not None and not isinstance(af, str):
                self.errors.append(f"{name} alt_function must be a string (STM32 macro)")

    def _validate_communication_section(self):
        comm = self.config.get("communication", {})
        for uart in comm.get("uart", []):
            if not uart.get("instance"):
                self.errors.append("uart missing instance")
            if not isinstance(uart.get("enabled"), bool):
                self.errors.append(f"{uart.get('instance','?')} uart enabled must be bool")
            if uart.get("enabled") and (not isinstance(uart.get("baudrate"), int) or uart.get("baudrate") <= 0):
                self.errors.append(f"{uart.get('instance') or 'uart'} invalid baudrate")
        for i2c in comm.get("i2c", []):
            if not i2c.get("instance"):
                self.errors.append("i2c missing instance")
            if not isinstance(i2c.get("enabled"), bool):
                self.errors.append(f"{i2c.get('instance','?')} i2c enabled must be bool")
            if i2c.get("enabled") and (not isinstance(i2c.get("speed"), int) or i2c.get("speed") <= 0):
                self.errors.append(f"{i2c.get('instance') or 'i2c'} invalid speed")

    def _validate_timers_section(self):
        timers = self.config.get("timers", [])
        for t in timers:
            if not t.get("instance"):
                self.errors.append("timer missing instance")
            if not isinstance(t.get("enabled"), bool):
                self.errors.append(f"{t.get('instance','?')} timer enabled must be bool")
            if t.get("enabled"):
                psc = t.get("prescaler")
                per = t.get("period")
                if not isinstance(psc, int) or psc <= 0:
                    self.errors.append(f"{t.get('instance')} invalid prescaler")
                if not isinstance(per, int) or per <= 0:
                    self.errors.append(f"{t.get('instance')} invalid period")
                if t.get("mode") == "pwm" and ("duty_cycle" not in t or "channel" not in t):
                    self.errors.append(f"{t.get('instance')} pwm needs duty_cycle and channel")

    def print_summary(self):
        board = self.config.get("board", {})
        print("\n--- config summary ---")
        print(f"board     : {board.get('name')}")
        print(f"mcu       : {board.get('mcu')}")
        print(f"sysclock  : {board.get('clock_freq')} hz")

        pins = self.config.get("gpio", {}).get("pins", [])
        print(f"\ngpio pins ({len(pins)})")
        for p in pins:
            alt = f", alt_fn: {p['alt_function']}" if "alt_function" in p else ""
            print(f"  {p.get('pin','n/a'):<5} | dir: {p.get('direction','n/a'):<18} | pull: {p.get('pull','n/a'):<9} | speed: {p.get('speed','n/a')}{alt}")

        comm = self.config.get("communication", {})
        if comm.get("uart"):
            print(f"\nuart ({len(comm['uart'])})")
            for u in comm["uart"]:
                status = "on" if u["enabled"] else "off"
                print(f"  {u['instance']}: {status}, baud {u['baudrate']}, tx {u['tx_pin']}, rx {u['rx_pin']}")
        if comm.get("i2c"):
            print(f"\ni2c ({len(comm['i2c'])})")
            for i in comm["i2c"]:
                status = "on" if i["enabled"] else "off"
                print(f"  {i['instance']}: {status}, speed {i['speed']} hz, scl {i['scl_pin']}, sda {i['sda_pin']}")

        timers = self.config.get("timers", [])
        if timers:
            print(f"\ntimers ({len(timers)})")
            for t in timers:
                status = "on" if t["enabled"] else "off"
                print(f"  {t['instance']}: {status}, mode {t['mode']}, presc {t['prescaler']}, period {t['period']}")
        print("\n--- end summary ---\n")

    def generate_c_file(self, output="peripheral_init.c"):
        board_name = self.config.get("board", {}).get("name", "unknown_board")
        with open(output, "w") as f:
            f.write(f"/* auto-generated for {board_name} */\n")
            f.write("#include \"stm32f4xx_hal.h\"\n\n")
            self._write_gpio_c(f)
            self._write_uart_c(f)
            self._write_i2c_c(f)
            self._write_timer_c(f)
            f.write("void initialize_peripherals(void) {\n")
            f.write("    init_gpio();\n")
            comm = self.config.get("communication", {})
            for uart in comm.get("uart", []):
                if uart.get("enabled"):
                    f.write(f"    init_{uart['instance']}();\n")
            for i2c in comm.get("i2c", []):
                if i2c.get("enabled"):
                    f.write(f"    init_{i2c['instance']}();\n")
            for timer in self.config.get("timers", []):
                if timer.get("enabled"):
                    f.write(f"    init_{timer['instance']}();\n")
            f.write("}\n")
        print(f"c code written to {output}")

    def _write_gpio_c(self, f):
        f.write("static void init_gpio(void) {\n")
        f.write("    GPIO_InitTypeDef GpioStruct = {0};\n\n")
        seen_ports = set()
        for pin in self.config["gpio"]["pins"]:
            port = pin["pin"][1]
            num = pin["pin"][2:]
            if port not in seen_ports:
                f.write(f"    __HAL_RCC_GPIO{port}_CLK_ENABLE();\n")
                seen_ports.add(port)
            f.write(f"    /* {pin['pin']}: {pin.get('comment', '')} */\n")
            f.write(f"    GpioStruct.Pin = GPIO_PIN_{num};\n")
            if "alt_function" in pin:
                f.write("    GpioStruct.Mode = GPIO_MODE_AF_PP;\n")
                af_macro = pin.get("alt_function")
                f.write(f"    GpioStruct.Alternate = {af_macro};\n")
            else:
                if pin["direction"] == "input":
                    f.write("    GpioStruct.Mode = GPIO_MODE_INPUT;\n")
                elif pin["direction"] == "output_open_drain":
                    f.write("    GpioStruct.Mode = GPIO_MODE_OUTPUT_OD;\n")
                else:
                    f.write("    GpioStruct.Mode = GPIO_MODE_OUTPUT_PP;\n")
            f.write(f"    GpioStruct.Pull = {pull_map[pin['pull']]};\n")
            f.write(f"    GpioStruct.Speed = {speed_map[pin['speed']]};\n")
            f.write(f"    HAL_GPIO_Init(GPIO{port}, &GpioStruct);\n\n")
        f.write("}\n\n")

    def _write_uart_c(self, f):
        for uart in self.config.get("communication", {}).get("uart", []):
            if not uart.get("enabled"):
                continue
            inst = uart["instance"]
            hname = handle_var_name("hu", inst)
            f.write(f"UART_HandleTypeDef {hname};\n")
            f.write(f"void init_{inst}(void) {{\n")
            f.write(f"    {hname}.Instance = {inst};\n")
            f.write(f"    {hname}.Init.BaudRate = {uart['baudrate']};\n")
            f.write(f"    {hname}.Init.WordLength = UART_WORDLENGTH_8B;\n")
            parity_map = {"none": "UART_PARITY_NONE", "even": "UART_PARITY_EVEN", "odd": "UART_PARITY_ODD"}
            parity = uart.get("parity", "none")
            f.write(f"    {hname}.Init.Parity = {parity_map[parity]};\n")
            f.write(f"    {hname}.Init.StopBits = UART_STOPBITS_{uart['stop_bits']};\n")
            f.write(f"    {hname}.Init.Mode = UART_MODE_TX_RX;\n")
            f.write(f"    {hname}.Init.HwFlowCtl = UART_HWCONTROL_NONE;\n")
            f.write(f"    {hname}.Init.OverSampling = UART_OVERSAMPLING_16;\n")
            f.write(f"    if (HAL_UART_Init(&{hname}) != HAL_OK) {{\n        Error_Handler();\n    }}\n")
            f.write("}\n\n")

    def _write_i2c_c(self, f):
        for i2c in self.config.get("communication", {}).get("i2c", []):
            if not i2c.get("enabled"):
                continue
            inst = i2c["instance"]
            hname = handle_var_name("hi", inst)
            f.write(f"I2C_HandleTypeDef {hname};\n")
            f.write(f"void init_{inst}(void) {{\n")
            f.write(f"    {hname}.Instance = {inst};\n")
            f.write(f"    {hname}.Init.ClockSpeed = {i2c['speed']};\n")
            f.write(f"    {hname}.Init.DutyCycle = I2C_DUTYCYCLE_2;\n")
            f.write(f"    {hname}.Init.OwnAddress1 = 0;\n")
            f.write(f"    {hname}.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;\n")
            f.write(f"    {hname}.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;\n")
            f.write(f"    {hname}.Init.OwnAddress2 = 0;\n")
            f.write(f"    {hname}.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;\n")
            f.write(f"    {hname}.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;\n")
            f.write(f"    if (HAL_I2C_Init(&{hname}) != HAL_OK) {{\n        Error_Handler();\n    }}\n")
            f.write("}\n\n")

    def _write_timer_c(self, f):
        for timer in self.config.get("timers", []):
            if not timer.get("enabled"):
                continue
            inst = timer["instance"]
            hname = handle_var_name("ht", inst)
            f.write(f"TIM_HandleTypeDef {hname};\n")
            f.write(f"void init_{inst}(void) {{\n")
            f.write(f"    {hname}.Instance = {inst};\n")
            f.write(f"    {hname}.Init.Prescaler = {timer['prescaler'] - 1};\n")
            f.write(f"    {hname}.Init.CounterMode = TIM_COUNTERMODE_UP;\n")
            f.write(f"    {hname}.Init.Period = {timer['period'] - 1};\n")
            f.write(f"    {hname}.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;\n")
            f.write(f"    if (HAL_TIM_Base_Init(&{hname}) != HAL_OK) {{\n        Error_Handler();\n    }}\n")
            if timer.get("mode") == "pwm":
                f.write(f"    // pwm out ch {timer['channel']} duty {timer['duty_cycle']}%\n")
            f.write("}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="parse yaml and make stm32 init c code")
    parser.add_argument("config_file", help="yaml config file path")
    parser.add_argument("-o", "--output", default="peripheral_init.c", help="name of output c file")
    parser.add_argument("-s", "--summary", action="store_true", help="show summary and quit")
    parser.add_argument("-v", "--validate-only", action="store_true", help="validate only no code")
    args = parser.parse_args()

    gen = configparser(args.config_file)
    gen.load_and_validate()

    if args.summary:
        gen.print_summary()
        sys.exit(0)
    if args.validate_only:
        print("validation successful no code generated")
        sys.exit(0)

    gen.generate_c_file(args.output)
