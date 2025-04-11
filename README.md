# Raspberry Pi Camera Controller

A touchscreen-based controller for multiple PTZ cameras using VISCA over IP protocol.

## Features

- Control up to 3 PTZ cameras via VISCA over IP
- Analog joystick support for pan, tilt, and zoom
- Touch-friendly UI optimized for 800x480 Raspberry Pi displays
- Camera configuration management
- On-screen controls for camera movement

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- 800x480 touchscreen display
- MCP3008 analog-to-digital converter
- Analog joystick

## Installation

1. Clone this repository on your Raspberry Pi:

`git clone https://github.com/Pentonit/RPIptz-visca-ip`  
`cd RPIptz-visca-ip`

2. make sure you have the virtual environment installed on your raspberry pi:

`sudo apt-get update`  
`sudo apt-get install python3-venv`

3. make sure the run script is executable:

`chmod +x run.sh`

4. Connect your hardware:
- Connect the MCP3008 to the Raspberry Pi's SPI pins
- Connect the analog joystick to the MCP3008
- Connect the touchscreen display

5. Configure your cameras:
- Edit the `config/config.yaml` file to match your camera IP addresses and ports
- Or use the configuration UI in the application

6. Run the application:

`./run.sh`

## Joystick Configuration

The default configuration assumes:
- X-axis connected to MCP3008 channel 0
- Y-axis connected to MCP3008 channel 1
- Zoom control connected to MCP3008 channel 2

You can modify these settings in the `config/config.yaml` file.

## License

MIT