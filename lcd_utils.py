from machine import SoftI2C, Pin
from i2c_lcd import I2cLcd
import time
import uasyncio as asyncio

# Initialize I2C
i2c = SoftI2C(sda=Pin(8), scl=Pin(9), freq=400000)  # SDA to GPIO 8, SCL to GPIO 9
devices = i2c.scan()

if devices:
    for device in devices:
        print("I2C device found at address:", hex(device))
else:
    print("No I2C device found")

# Use the detected I2C address (replace with your actual address)
LCD_I2C_ADDR = 0x27  # The address found by the scan

# Define the LCD parameters
lcd = I2cLcd(i2c, LCD_I2C_ADDR, 2, 16)  # Adjust for your LCD's number of rows and columns

async def clear_display():
    lcd.clear()


async def display_message(
    message,
    line=0,
    display_time=None,
    scroll_time=0.3,
    clear_time=None,
    clear_before=False,
    repeat=True,
    allow_scroll=True  # New boolean parameter to control scrolling
):
    """
    Display a message on the LCD. Scrolls the text if it exceeds the LCD column width
    and scrolling is allowed.

    :param message: The message to display.
    :param line: The line on the LCD to display or scroll the text.
    :param display_time: Total time to display the message before clearing (in seconds).
    :param scroll_time: Time delay between each scroll step (in seconds). Used for scrolling.
    :param clear_time: Time to wait after display before clearing the message (in seconds).
    :param clear_before: If True, clears the display before displaying the message.
    :param repeat: If True, scrolls the message repeatedly until display_time expires.
    :param allow_scroll: If True, allows the message to scroll if it's longer than the display width.
                         If False, displays the message without scrolling, truncating if necessary.
    """
    line = max(0, min(line, lcd.num_lines - 1))  # Ensure line is within valid bounds

    # Clear LCD before displaying if requested
    if clear_before:
        lcd.clear()

    if len(message) <= lcd.num_columns or not allow_scroll:
        # Message fits within the display or scrolling is not allowed
        lcd.move_to(0, line)
        # If message is longer than display and scrolling is disabled, truncate the message
        if len(message) > lcd.num_columns and not allow_scroll:
            display_str = message[:lcd.num_columns]
            lcd.putstr(display_str)
            print(f"Displayed (truncated): {display_str}")  # Debug statement
        else:
            lcd.putstr(message)
            print(f"Displayed: {message}")  # Debug statement

        # Wait for display_time before clearing
        if display_time is not None:
            await asyncio.sleep(display_time)
            if clear_time is not None:
                await asyncio.sleep(clear_time)
            lcd.move_to(0, line)
            lcd.putstr(" " * lcd.num_columns)
    else:
        if not allow_scroll:
            # Scrolling is disabled but message is longer; truncate and display
            lcd.move_to(0, line)
            display_str = message[:lcd.num_columns]
            lcd.putstr(display_str)
            print(f"Displayed (truncated without scrolling): {display_str}")  # Debug statement

            # Wait for display_time before clearing
            if display_time is not None:
                await asyncio.sleep(display_time)
                if clear_time is not None:
                    await asyncio.sleep(clear_time)
                lcd.move_to(0, line)
                lcd.putstr(" " * lcd.num_columns)
            return  # Exit the function after displaying truncated message

        # Message needs to be scrolled
        padded_text = message + " " * lcd.num_columns
        scroll_length = len(padded_text) - lcd.num_columns + 1  # Correct scroll length

        start_time = time.ticks_ms()  # Record the start time

        while True:
            # Scroll the message once
            for i in range(scroll_length):
                lcd.move_to(0, line)
                lcd.putstr(padded_text[i:i + lcd.num_columns])
                await asyncio.sleep(scroll_time)

                # Check if display_time has elapsed
                if display_time is not None:
                    elapsed_time = (time.ticks_diff(time.ticks_ms(), start_time)) / 1000  # Convert to seconds
                    if elapsed_time >= display_time:
                        break  # Exit the for loop

            # After the for loop
            if display_time is not None:
                elapsed_time = (time.ticks_diff(time.ticks_ms(), start_time)) / 1000  # Update elapsed time
                if elapsed_time >= display_time:
                    break  # Exit the while loop

            if not repeat:
                break  # Exit the while loop if repeat is False

            # If repeating and display_time hasn't elapsed, continue scrolling

        # Optionally clear after scrolling
        if clear_time is not None:
            await asyncio.sleep(clear_time)
        lcd.move_to(0, line)
        lcd.putstr(" " * lcd.num_columns)



async def scroll_text(text, line=0, display_time=0.3, clear_before=False, clear_after=True):
    """
    Scroll text horizontally across the specified line on the LCD asynchronously.

    :param text: The text to scroll.
    :param line: The line on the LCD to scroll the text.
    :param display_time: Time delay between each scroll step (in seconds).
    :param clear_after: If True, clears the LCD line after scrolling. Default is True.
    """
    padded_text = text + " " * lcd.num_columns
    display_length = len(text) + lcd.num_columns
    
    if clear_before:
        lcd.clear()

    for i in range(display_length):
        lcd.move_to(0, line)
        lcd.putstr(padded_text[i:i + lcd.num_columns])
        await asyncio.sleep(display_time)

    if clear_after:
        lcd.move_to(0, line)
        lcd.putstr(" " * lcd.num_columns)

