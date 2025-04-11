from gpiozero import MCP3008
import time
import threading

class JoystickController:
    def __init__(self, x_pin, y_pin, zoom_pin, deadzone=0.1):
        # Initialize analog inputs for joystick
        self.x_axis = MCP3008(x_pin)
        self.y_axis = MCP3008(y_pin)
        self.zoom_axis = MCP3008(zoom_pin)
        
        self.deadzone = deadzone
        self.running = False
        self.callback = None
        self.thread = None
    
    def start_monitoring(self, callback):
        """Start monitoring joystick movements"""
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring joystick movements"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Monitor joystick movements in a separate thread"""
        while self.running:
            # Read joystick values (0 to 1)
            x_value = self.x_axis.value
            y_value = self.y_axis.value
            zoom_value = self.zoom_axis.value
            
            # Convert to -1 to 1 range
            x = (x_value * 2) - 1
            y = (y_value * 2) - 1
            zoom = (zoom_value * 2) - 1
            
            # Apply deadzone
            x = 0 if abs(x) < self.deadzone else x
            y = 0 if abs(y) < self.deadzone else y
            zoom = 0 if abs(zoom) < self.deadzone else zoom
            
            # Call the callback with joystick values
            if self.callback:
                self.callback(x, y, zoom)
            
            # Sleep to avoid high CPU usage
            time.sleep(0.05)
    
    def get_values(self):
        """Get current joystick values"""
        # Read joystick values (0 to 1)
        x_value = self.x_axis.value
        y_value = self.y_axis.value
        zoom_value = self.zoom_axis.value
        
        # Convert to -1 to 1 range
        x = (x_value * 2) - 1
        y = (y_value * 2) - 1
        zoom = (zoom_value * 2) - 1
        
        # Apply deadzone
        x = 0 if abs(x) < self.deadzone else x
        y = 0 if abs(y) < self.deadzone else y
        zoom = 0 if abs(zoom) < self.deadzone else zoom
        
        return x, y, zoom