import uasyncio as asyncio
import ntptime
import time

last_sync = 0
sync_interval = 3600  # Sync every hour (3600 seconds)

def synchronize_time():
    global last_sync
    try:
        ntptime.settime()
        last_sync = time.time()
        print("Time synchronized with NTP server.")
    except Exception as e:
        print("Failed to synchronize time:", e)

async def periodic_time_sync():
    while True:
        current_time = time.time()
        if current_time - last_sync > sync_interval:
            synchronize_time()
        await asyncio.sleep(60)  # Check every minute

def get_current_datetime_string():
    current_time = time.localtime()
    datetime_str = f"{current_time[0]}-{current_time[1]:02}-{current_time[2]:02} {current_time[3]:02}:{current_time[4]:02}:{current_time[5]:02}"
    return datetime_str



