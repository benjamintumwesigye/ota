from machine import Pin
from lcd_utils import display_message
import ure as re
from wifi_connect import *
from wifi_monitor import wifi_monitor
from api_calls import *
import uasyncio as asyncio
from messages import *
import server
from access_point import *
from utils import *
from time_sync import periodic_time_sync
import gc

gc.collect()
print("Free memory:", gc.mem_free())

ALARM_ON = False
connect_to_wifi()
asyncio.run(welcome())
srv = server.start_server()

# Initialize the Siren pin
SIREN_PIN = Pin(3, Pin.OUT)

# Initialize the Button pin
BTN_PIN = Pin(43, Pin.IN, Pin.PULL_UP)

# Define the list of button pins and their corresponding room names
BUTTON_PINS = [
    (18, "Room 01"),
    (16, "Room 02"),
    (15, "Room 03"),
    (7, "Room 04"),
    (6, "Room 05"),
    (4, "Room 06"),
    (5, "Room 07"),
    (47, "Room 08"),
    (48, "Room 09"),
    (38, "Room 10"),
    (39, "Room 11"),
    (40, "Room 12"),
    (41, "Room 13"),
    (42, "Room 14"),
    (44, "Room 15"),
]

# Initialize buttons
buttons = {}
for pin_num, _ in BUTTON_PINS:
    try:
        buttons[pin_num] = Pin(pin_num, Pin.IN, Pin.PULL_UP)
    except ValueError as e:
        print(f"Error initializing pin {pin_num}: {e}")

async def wifi():
    # Connect to Wi-Fi
    connected = is_connected()
    if not connected:
        print("Cannot proceed without Wi-Fi connection.")
        return

    # Start Wi-Fi monitor task
    asyncio.create_task(wifi_monitor())

# Define the alarm function
async def set_alarm(room):
    config = load_config()
    if not config:
        print("Cannot load Wi-Fi credentials from config file.")
        return

    TEST_MODE = config.get('test_mode', False)
    print(f"Alarm is ON for {room}")
    global ALARM_ON
    ALARM_ON = True	
    SIREN_PIN.value(1)  # Turn the Siren on
    await alarm_msg(room)
    if not TEST_MODE:
        await send_alarm_to_mother(room)
    else:
        await asyncio.sleep(2)
        SIREN_PIN.value(0)
        ALARM_ON = False
        await defaultDisplay()

async def set_mother_alarm():
    config = load_config()
    if config is None:
        print("Failed to load configuration file.")
        return False
    if config.get('isMother') == True:
        # Retrieve the 'mother_alarms' list
        mother_alarms = config.get('mother_alarms', [])
        
        # Find and update the matching alarm
        for alarm in mother_alarms:
            if alarm.get('ring') == True:
                global ALARM_ON
                ALARM_ON = True
                SIREN_PIN.value(1)  # Turn the Siren on

                # Ensure TEST_MODE is defined
                TEST_MODE = config.get('mode') == 'test'

                await mother_alarm_msg(alarm.get('block_name'), alarm.get('room'))
                
                if not TEST_MODE:
                    print('Sending to cloud...')
                    # Place your code to send data to the cloud here
                else:
                    await asyncio.sleep(3)
                    SIREN_PIN.value(0)
                    await defaultDisplay()
                    ALARM_ON = False 
                break

     

def server_check():
    if srv is None:
        print("Server failed to start.")
        return

def reset():
    global ALARM_ON
    ALARM_ON = False
    reset_mother()
    asyncio.create_task(defaultDisplay())

        
async def set_mother_alarm_loop():
    while True:
        if BTN_PIN.value() == 0:
            SIREN_PIN.value(0)
            print(ALARM_ON)
            if not ALARM_ON:
                await view_connection()
            else:
                await defaultDisplay()
                reset()
                    
        await set_mother_alarm()
        await asyncio.sleep(0.5)


        
async def start_socket_server():
    """
    Initializes and starts the asynchronous socket server.
    """
    global ap_ip
    # Ensure that AP is started before binding the socket
    if ap_ip is None:
        print("AP IP is not available. Starting AP...")
        ap_obj, ap_ip = await start_access_point()
    
    try:
        # Start the server using host and port
        server = await asyncio.start_server(handle_client, host=ap_ip, port=80)
        print('Socket Listening on port 80')

        # Keep the coroutine running to accept connections
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, effectively keeping the coroutine running
    except Exception as e:
        print("Failed to start socket server:", e)        


async def handle_button_press(pin_num):
    config = load_config()
    number_of_rooms_str = config.get('number_of_rooms', '')
    
    number_of_rooms = number_of_rooms_str.split(',')
    room_index = None
    for index, (pin, _) in enumerate(BUTTON_PINS):
        if pin == pin_num:
            room_index = index
            break
    
    if room_index is not None:
        # Check if room_index is within the bounds of number_of_rooms
        if room_index < len(number_of_rooms):
            dynamic_room_label = number_of_rooms[room_index]  # e.g., 'R7'
            display_message_str = f"Room {dynamic_room_label}"
        else:
            # If not enough room labels, default to "Room Unknown"
            display_message_str = "Room Unknown"
            print(f"No room label available for button pin {pin_num} at index {room_index}")
    else:
        # If button pin not found in BUTTON_PINS
        display_message_str = "Room Unknown"
        print(f"Button pin {pin_num} not found in BUTTON_PINS")
    
    # Trigger alarm with dynamic room label
    asyncio.create_task(set_alarm(display_message_str))

 
async def main():
    await wifi()
    check_free_space()
    connect_to_wifi()
    
    srv = server.start_server()
    asyncio.create_task(defaultDisplay())

    # Start the Access Point
    global ap, ap_ip
    ap, ap_ip = await start_access_point()
    
    # Schedule the socket server
    asyncio.create_task(start_socket_server())

    # Sync time every 1Hr
    asyncio.create_task(periodic_time_sync())
    
    # Schedule background tasks
    config = load_config()
    if config is None:
        print("Failed to load configuration file.")
        return False
    if config.get('isMother') == True:
        asyncio.create_task(set_mother_alarm_loop())
    
    # Start periodic pinging every hour
    asyncio.create_task(periodic_ping())
    
    print("Waiting for button presses...")
    while True:
        # Iterate over each button to check for presses
        for pin_num, _ in BUTTON_PINS:
            if buttons[pin_num].value() == 0:  # Button pressed (active low)
                asyncio.create_task(handle_button_press(pin_num))
                await asyncio.sleep(1)  
                break  # Exit loop to avoid multiple alarms at once
       
        # Independent listener for BTN_PIN
        if BTN_PIN.value() == 0:
            SIREN_PIN.value(0)
            print(ALARM_ON)
            if not ALARM_ON:
                asyncio.create_task(view_connection())
            else:
                reset()
        
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting program")
        server.stop_server(srv)
        # Add cleanup code if necessary


