# Raspberry Pi Camera Controller

A touchscreen-based controller for multiple PTZ cameras using VISCA over IP protocol.

## Features

- Control up to 3 PTZ cameras via VISCA over IP
- Analog joystick support for pan, tilt, and zoom
- Game controller support (Xbox/PS style via pygame), with selectable device and configurable axis mapping
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

4. Connect your hardware (one or both):
- Connect the MCP3008 to the Raspberry Pi's SPI pins
- Connect the analog joystick to the MCP3008
- Connect the touchscreen display
- Optional: connect a USB/Bluetooth game controller (e.g., Xbox/PS)

5. Configure your cameras:
- Edit the `config/config.yaml` file to match your camera IP addresses and ports
- Or use the configuration UI in the application

6. Run the application:

`./run.sh`

If you use a game controller, open the Controllers tab to select a device and set mapping.

### Re-download/Reset helper

If you need to nuke the local copy and pull a fresh one, use:

```bash
chmod +x redownload.sh
./redownload.sh
```

You can also pass a custom target directory and branch:

```bash
./redownload.sh /home/pi/RPIptz-visca-ip main
```

### Notes on PyQt5 installation on Raspberry Pi

- This project uses PyQt5. Building PyQt5 from source on Raspberry Pi can be extremely slow or hang.
- The `run.sh` script is set up to prefer pre-built wheels from `piwheels.org` and will try several compatible `PyQt5` versions. If no wheel is available, it falls back to installing `python3-pyqt5` via `apt`.
- If you're on a 64-bit Raspberry Pi OS where piwheels doesn't provide a matching wheel, the apt fallback should still work.

## Joystick Configuration

The default configuration assumes:
- X-axis connected to MCP3008 channel 0
- Y-axis connected to MCP3008 channel 1
- Zoom control connected to MCP3008 channel 2

You can modify these settings in the `config/config.yaml` file.

## Game Controller Mapping

The default mapping uses left stick for pan/tilt and right stick vertical for zoom. You can change these in the application under the Controllers tab, which will persist to `config/config.yaml` under `gamepad.mapping`.

If running on Raspberry Pi Lite, you may need packages for SDL/pygame:

```bash
sudo apt-get update
sudo apt-get install -y libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0
```

On Raspberry Pi OS with the official 7" touchscreen, ensure Qt uses the EGLFS or KMS backend. If launching from the console without X, set:

```bash
export QT_QPA_PLATFORM=eglfs
```

If using a desktop session, omit the above and run normally.

## License

MIT