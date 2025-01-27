import urequests
import uasyncio as asyncio
import network
import time
import json
import ujson
from wifi_connect import connect_to_wifi
from utils import *
from time_sync import get_current_datetime_string

headers = {'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0 (platform; rv:gecko-version) Gecko/gecko-trail Firefox/firefox-version'}

async def send_alarm_to_mother(room):
    """
    Asynchronously sends an alarm to mother devices for a specific room.
    """
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        return
    
    block_name = config.get('block_name')
    mother_ips_str = config.get('mothers')  # Get the mother IPs as a string

    if not block_name or not room:
        print("Block name or room number not found in configuration.")
        return

    if not mother_ips_str:
        print("Mother IPs not found in configuration.")
        return

    # Connect to Wi-Fi
    connected = connect_to_wifi()
    if not connected:
        print("Cannot proceed without Wi-Fi connection.")
        return

    # Split mother IPs into a list
    mother_ips = [ip.strip() for ip in mother_ips_str.split(',')]

    # Send alarm to mother servers
    await send_alarm_to_mothers(block_name, room, mother_ips)

async def send_alarm_to_mothers(block_name, room, mother_ips, retries=2, delay=1):
    """
    Asynchronously sends alarms to multiple mother devices and updates the configuration.
    """
    datetime_str = get_current_datetime_string()
    headers = {'Content-Type': 'application/json'}

    for ip in mother_ips:
        url = f"http://{ip}/api/mother/alarm"
        reference = gen_reference()
        payload = {
            "block_name": block_name,
            "room": room,
            "date": datetime_str,
            "reference": reference
        }

        isSent = False  # Default to False

        for attempt in range(1, retries + 1):
            try:
                print(f"Attempt {attempt}: Sending alarm to mother server at {ip}...")
                response = urequests.put(url, data=json.dumps(payload), headers=headers)
                if response.status_code == 200:
                    isSent = True
                    print(f"Successfully sent alarm to {ip}: {response.status_code} - {response.text}")
                    response.close()
                    break  # Exit the retry loop on success
                else:
                    print(f"Failed to send alarm to {ip}: {response.status_code} - {response.text}")
                response.close()
            except Exception as e:
                print(f"Error sending to {ip}: {e}")

            # Wait before the next retry
            await asyncio.sleep(delay)

        # Update 'last_alarm' in config
        await update_last_alarm(room, datetime_str, reference, isSent)
        
        # Yield control to the event loop
        await asyncio.sleep(0)

async def update_last_alarm(room, datetime_str, reference, isSent):
    """
    Asynchronously updates the 'last_alarm' key in the configuration file.
    """
    config = load_config()
    if config is None:
        print("Failed to load configuration for updating 'last_alarm'.")
        return

    # Ensure 'last_alarm' is a list
    if 'last_alarm' not in config or not isinstance(config['last_alarm'], list):
        config['last_alarm'] = []

    # Create the alarm entry
    alarm_entry = {
        "room": room,
        "date": datetime_str,
        "reference": reference,
        "isSent": isSent
    }

    # Append the new alarm entry
    config['last_alarm'].append(alarm_entry)
    print(f"Updated 'last_alarm' with: {alarm_entry}")

    # Save the updated configuration
    try:
        save_config(config)
    except Exception as e:
        print(f"Error updating 'last_alarm' in configuration: {e}")
  
  
async def ping_server_call(retries=1, backoff_factor=2):
   
    url = "https://demo.erp.arxcess.com/arxcess-erp-api/open-accommodation-machines/ping"
    config = load_config()
    
    if not config:
        print("Failed to load configuration.")
        return False
    
    code = config.get('machine_code')
    token = config.get('machine_token')
    ipAddress = config.get('ip_address')
    
    if not code or not token or not ipAddress:
        print("Machine code or token missing in configuration.")
        return False
    
    payload = {
        "ipAddress": ipAddress
    }
    full_url = f"{url}?code={code}&token={token}"
    
    print(f"Pinging server at: {full_url}")
    
    delay = 1  # Initial delay in seconds
    
    for attempt in range(1, retries + 1):
        try:
            response = urequests.put(full_url,data=json.dumps(payload),headers=headers)
            if response.status_code == 200:
                print("Ping successful:", response.text)
                response.close()
                return True
            else:
                print(f"Ping failed with status {response.status_code}: {response.text}")
                response.close()
        except Exception as e:
            print(f"Error during ping (Attempt {attempt}): {e}")
        
        if attempt < retries:
            print(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            delay *= backoff_factor  # Exponential backoff
    
    print("All ping attempts failed.")
    return False


async def periodic_ping(interval=60):
    while True:
        print("Starting periodic ping...")
        success = await ping_server_call()
        if success:
            print("Periodic ping successful.")
        else:
            print("Periodic ping failed.")
        
        print(f"Waiting for {interval} seconds before next ping.")
        await asyncio.sleep(interval)








