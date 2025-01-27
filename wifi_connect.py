import network
import ujson
import time
import uasyncio as asyncio

wlan = network.WLAN(network.STA_IF)

def connect_to_wifi():
    """
    Connects to Wi-Fi using credentials from 'wifi_config.json'.
    """
    # Load Wi-Fi credentials
    try:
        with open('wifi_config.json', 'r') as f:
            credentials = ujson.load(f)
        ssid = credentials.get('ssid')
        password = credentials.get('password')

        if not ssid or not password:
            print("Error: SSID or password is missing in the configuration.")
            return False

    except Exception as e:
        print("Error reading Wi-Fi credentials:", e)
        return False
    
    
    wlan.active(True)

    # Check if already connected
    if wlan.isconnected():
        print("Already connected to Wi-Fi:", wlan.ifconfig())
        return True

    # Attempt to connect
    print(f"Connecting to Wi-Fi SSID='{ssid}'...")
    wlan.active(False)
    wlan.active(True)
    try:
        wlan.connect(ssid, password)
    except Exception as e:
        print("Wifi Error:", e)    

    # Wait for connection with timeout
    max_wait = 15  # seconds
    while max_wait > 0:
        if wlan.isconnected():
            print("Successfully connected to Wi-Fi!")
            print("Network configuration:", wlan.ifconfig())
            return True
        time.sleep(1)
        max_wait -= 1
        print(f"Waiting for connection... {max_wait} seconds remaining.")

    print("Failed to connect to Wi-Fi.")
    return False

def is_connected():
    return wlan.isconnected()

def get_ip():
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    else:
        return None
