import network
import ujson
import uasyncio as asyncio
from utils import *

wlan = network.WLAN(network.STA_IF)

async def wifi_monitor():
    config = load_config()
    """
    Monitors the Wi-Fi connection and attempts to reconnect if disconnected.
    Retrieves Wi-Fi credentials from 'wifi_config.json'.
    """

    wlan.active(True)
    failure_count = 0

    # Load Wi-Fi credentials
    if config:
        ssid = config.get('ssid')
        password = config.get('password')

    while True:
        if not wlan.isconnected():
            wlan.active(False)
            wlan.active(True)
            print("Wi-Fi connection lost. Attempting to reconnect...")
                # Update the config file with the ip_address
            if config:
                config['ip_address'] = ""
                save_config(config)
            wlan.disconnect()
            wlan.connect(ssid, password)

            # Wait for reconnection
            max_wait = 15  # seconds
            while max_wait > 0:
                if wlan.isconnected():
                    if config:
                        config['ip_address'] = wlan.ifconfig()[0]
                        save_config(config)
                    failure_count = 0               
                    print("Reconnected to Wi-Fi!")
                    break
                await asyncio.sleep(1)
                max_wait -= 1
                print(f"Reconnecting... {max_wait} seconds remaining.")

            else:
                failure_count += 1
                print(f"Failed to reconnect to Wi-Fi. Failure count: {failure_count}")

                # Optional: Reboot the device after a certain number of failures
                if failure_count >= 5:
                    print("Maximum reconnection attempts reached. Rebooting...")
                    import machine
                    machine.reset()
        else:
            # Reset failure count if connected
            failure_count = 0

        await asyncio.sleep(5)  # Wait before checking again

