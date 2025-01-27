from lcd_api import LcdApi
from machine import I2C, Pin
from time import sleep_ms

# Default I2C address for the LCD backpack
DEFAULT_I2C_ADDR = 0x27

class I2cLcd(LcdApi):
    """Implements an HD44780 character LCD connected via PCF8574 on I2C."""

    def __init__(self, i2c, i2c_addr=DEFAULT_I2C_ADDR, num_lines=2, num_columns=16):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08  # Set to 0x00 to turn off

        # Define LCD commands
        self.PCF8574_CMD_CLEAR_DISPLAY = 0x01
        self.PCF8574_CMD_RETURN_HOME = 0x02
        self.PCF8574_CMD_ENTRY_MODE_SET = 0x04
        self.PCF8574_CMD_DISPLAY_CONTROL = 0x08
        self.PCF8574_CMD_CURSOR_SHIFT = 0x10
        self.PCF8574_CMD_FUNCTION_SET = 0x20
        self.PCF8574_CMD_SET_CGRAM_ADDR = 0x40
        self.PCF8574_CMD_SET_DDRAM_ADDR = 0x80

        try:
            # Attempt to initialize the LCD
            self.init_lcd()
            print("LCD initialized successfully.")
        except OSError as e:
            print(f"LCD initialization failed: {e}")

    def init_lcd(self):
        sleep_ms(20)  # Wait for LCD to power up
        self._write_init(0x03)
        sleep_ms(5)
        self._write_init(0x03)
        sleep_ms(5)
        self._write_init(0x03)
        sleep_ms(5)
        self._write_init(0x02)  # Set to 4-bit mode
        sleep_ms(5)
        self.send_command(self.PCF8574_CMD_FUNCTION_SET | 0x08)  # 2-line display
        self.send_command(self.PCF8574_CMD_DISPLAY_CONTROL | 0x04)  # Display ON, cursor OFF
        self.clear()
        self.send_command(self.PCF8574_CMD_ENTRY_MODE_SET | 0x02)  # Increment cursor

    def _write_init(self, nibble):
        # Send initialization nibble
        self.i2c.writeto(self.i2c_addr, bytearray([nibble << 4 | self.backlight | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([nibble << 4 | self.backlight]))

    def send_command(self, cmd):
        # Send command to the LCD
        self._write_byte(cmd, 0)

    def send_data(self, data):
        # Send data to the LCD
        self._write_byte(data, 1)

    def _write_byte(self, data, mode):
        # Write a byte to the LCD
        upper_nibble = mode | (data & 0xF0) | self.backlight
        lower_nibble = mode | ((data << 4) & 0xF0) | self.backlight

        self.i2c.writeto(self.i2c_addr, bytearray([upper_nibble | 0x04]))  # Enable bit set
        self.i2c.writeto(self.i2c_addr, bytearray([upper_nibble & ~0x04]))  # Enable bit cleared
        self.i2c.writeto(self.i2c_addr, bytearray([lower_nibble | 0x04]))  # Enable bit set
        self.i2c.writeto(self.i2c_addr, bytearray([lower_nibble & ~0x04]))  # Enable bit cleared

    def clear(self):
        # Clear the LCD display
        self.send_command(self.PCF8574_CMD_CLEAR_DISPLAY)
        sleep_ms(2)

    def move_to(self, col, row):
        # Move cursor to a specific position
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.send_command(self.PCF8574_CMD_SET_DDRAM_ADDR | (col + row_offsets[row]))

    def putstr(self, string):
        # Display a string on the LCD
        for char in string:
            self.send_data(ord(char))

    def toggle_backlight(self, state):
        """Toggle backlight on or off"""
        self.backlight = 0x08 if state else 0x00
        # Refresh the display to reflect backlight change
        self.clear()

