from ota import OTAUpdater
from utils import load_config

config = load_config()

firmware_url = "https://github.com/kevinmcaleer/ota_test/main/"

# Load Wi-Fi credentials
if config:
    ssid = config.get('ssid')
    password = config.get('password')

    ota_updater = OTAUpdater(ssid, password, firmware_url, "test_ota.py")

    ota_updater.download_and_install_update_if_available()
