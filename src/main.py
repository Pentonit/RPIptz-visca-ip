#!/usr/bin/env python3
import sys
import os
import yaml
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from camera.camera_manager import CameraManager
from joystick.joystick_controller import JoystickController

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    else:
        # Default configuration
        default_config = {
            'cameras': [
                {'name': 'Camera 1', 'ip': '192.168.1.100', 'port': 52381},
                {'name': 'Camera 2', 'ip': '192.168.1.101', 'port': 52381},
                {'name': 'Camera 3', 'ip': '192.168.1.102', 'port': 52381}
            ],
            'joystick': {
                'x_pin': 0,  # Analog pin for X-axis
                'y_pin': 1,  # Analog pin for Y-axis
                'zoom_pin': 2,  # Analog pin for zoom control
                'deadzone': 0.1  # Deadzone for joystick
            }
        }
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        # Save default config
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file)
        return default_config

def main():
    # Load configuration
    config = load_config()
    
    # Initialize application
    app = QApplication(sys.argv)
    
    # Initialize camera manager
    camera_manager = CameraManager(config['cameras'])
    
    # Initialize joystick controller
    joystick = JoystickController(
        config['joystick']['x_pin'],
        config['joystick']['y_pin'],
        config['joystick']['zoom_pin'],
        config['joystick']['deadzone']
    )
    
    # Initialize main window
    window = MainWindow(camera_manager, joystick)
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()