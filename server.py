# server.py

import network
from time import sleep
import ujson  # Use ujson for MicroPython
from MicroWebSrv.microWebSrv import MicroWebSrv
import uasyncio as asyncio
from wifi_connect import get_ip
from utils import *

server_instance = None

# Define a GET route handler for the configuration
def config_get_handler(httpClient, httpResponse):
    try:
        with open('wifi_config.json', 'r') as f:
            config = f.read()
        # Return the config as JSON
        httpResponse.WriteResponseOk(
            headers=None,
            contentType="application/json",
            contentCharset="UTF-8",
            content=config
        )
    except Exception as e:
        print("Error reading config file:", e)
        httpResponse.WriteResponseInternalServerError()

# Define a PUT route handler to update the configuration
def config_put_handler(httpClient, httpResponse):
    # Get JSON payload from request
    content = httpClient.ReadRequestContentAsJSON()
    print(content)
    if content:
        try:
            # Write the content back to the config file
            with open('wifi_config.json', 'w') as f:
                ujson.dump(content, f)
            httpResponse.WriteResponseOk(
                headers=None,
                contentType="application/json",
                contentCharset="UTF-8",
                content=ujson.dumps({"message": "Configuration updated successfully"})
            )
        except Exception as e:
            print("Error writing to config file:", e)
            httpResponse.WriteResponseInternalServerError()
    else:
        # Bad request
        httpResponse.WriteResponseBadRequest({"error": "Invalid JSON data in request."})
        

# Define the POST route handler for '/mother/alarm'
def mother_alarm_handler(httpClient, httpResponse):
    # Read the JSON data from the request
    data = httpClient.ReadRequestContentAsJSON()
    if data:
        block_name = data.get('block_name')
        room = data.get('room')
        date = data.get('date')
        reference = data.get('reference')

        if block_name and room:
            print(f"Received alarm from Block: {block_name}, Room: {room}")
                # Load the existing config
            config = load_config()
            if config is None:
                # Handle error if config cannot be loaded
                response_data = {'error': 'Failed to load configuration file.'}
                httpResponse.WriteResponseInternalServerError(obj=response_data)
                return

            # Initialize 'mother_alarms' as a list if it doesn't exist
            if 'mother_alarms' not in config or not isinstance(config['mother_alarms'], list):
                config['mother_alarms'] = []

            # Create the new alarm entry
            new_alarm = {
                'block_name': block_name,
                'room': room,
                'date': date,
                'reference': reference,
                'ring': True
            }

            # Append the new alarm to the list
            config['mother_alarms'].append(new_alarm)
              # Save the updated config back to the file
            try:
                save_config(config)
                print("New alarm added to 'mother_alarms' in config file.")
                # Send a success response
                response_data = {'message': 'Alarm received and saved successfully'}
                httpResponse.WriteResponseJSONOk(obj=response_data)
            except Exception as e:
                print("Error updating config file:", e)
                response_data = {'error': 'Failed to update configuration file.'}
                httpResponse.WriteResponseInternalServerError(obj=response_data)

            # Send a success response
            response_data = {'message': 'Alarm received successfully'}
            httpResponse.WriteResponseJSONOk(obj=response_data)
        else:
            # Missing 'block_name' or 'room' in the data
            response_data = {'error': 'Missing "block_name" or "room" in request data'}
            httpResponse.WriteResponseBadRequest(obj=response_data)
    else:
        # Invalid or missing JSON data
        response_data = {'error': 'Invalid or missing JSON data'}
        httpResponse.WriteResponseBadRequest(obj=response_data)      

# Function to start the server
def start_server():
    global server_instance
    config = load_config()
    
    if server_instance is not None:
        print("Server is already running.")
        return server_instance

    # Connect to Wi-Fi
    ip_address = get_ip()
    if not ip_address:
        print("Cannot start server without Wi-Fi connection.")
        if config:
            config['ip_address'] = ""
            save_config(config)
        else:
            print("Failed to load config for updating IP address.")
        return None

    # Update the config file with the ip_address
    if config:
        config['ip_address'] = ip_address
        save_config(config)
    else:
        print("Failed to load config for updating IP address.")

    # Initialize the server with route handlers
    routeHandlers = [
        ("/api/config", "GET", config_get_handler),
        ("/api/config", "PUT", config_put_handler),
        ("/api/mother/alarm", "PUT", mother_alarm_handler)
    ]
    srv = MicroWebSrv(routeHandlers=routeHandlers)
    srv.Start(threaded=True)

    print(f"Server started! Access GET endpoint at http://{ip_address}/api/config")
    print(f"Server started! Access PUT endpoint at http://{ip_address}/api/config")
    print(f"Server started! Access PUT endpoint at http://{ip_address}/api/mother/alarm")

    server_instance = srv  # Store the server instance
    return srv

# Optional: Function to stop the server
def stop_server(srv):
    srv.Stop()
    print("Server stopped.")
