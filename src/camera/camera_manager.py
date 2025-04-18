from visca_over_ip import Camera
import logging

class CameraManager:
    def __init__(self, camera_configs):
        self.cameras = []
        self.active_camera_index = 0
        self.logger = logging.getLogger(__name__)
        
        # Initialize cameras from config
        for config in camera_configs:
            try:
                camera = Camera(config['ip'], config['port'])
                camera.name = config['name']
                camera.ip = config['ip']
                camera.port = config['port']
                self.cameras.append(camera)
                self.logger.info(f"Initialized camera: {config['name']} at {config['ip']}:{config['port']}")
            except Exception as e:
                self.logger.error(f"Failed to initialize camera {config['name']}: {str(e)}")
    
    def get_active_camera(self):
        """Get the currently active camera"""
        if not self.cameras:
            return None
        return self.cameras[self.active_camera_index]
    
    def set_active_camera(self, index):
        """Set the active camera by index"""
        if 0 <= index < len(self.cameras):
            self.active_camera_index = index
            return True
        return False
    
    def get_camera_list(self):
        """Get list of camera names"""
        return [camera.name for camera in self.cameras]
    
    def move_camera(self, pan_speed, tilt_speed):
        """Move the active camera with the given pan and tilt speeds"""
        camera = self.get_active_camera()
        if camera:
            try:
                camera.pantilt(pan_speed, tilt_speed)
                return True
            except Exception as e:
                self.logger.error(f"Error moving camera: {str(e)}")
        return False
    
    def zoom_camera(self, zoom_speed):
        """Zoom the active camera with the given speed"""
        camera = self.get_active_camera()
        if camera:
            try:
                if zoom_speed > 0:
                    # Try using the camera's built-in method for zoom tele
                    try:
                        camera.zoom_tele(min(abs(zoom_speed), 7))
                    except AttributeError:
                        # If that fails, try the standard method
                        camera.cmd_cam_zoom_tele()
                elif zoom_speed < 0:
                    # Try using the camera's built-in method for zoom wide
                    try:
                        camera.zoom_wide(min(abs(zoom_speed), 7))
                    except AttributeError:
                        # If that fails, try the standard method
                        camera.cmd_cam_zoom_wide()
                else:
                    # Try using the camera's built-in method for zoom stop
                    try:
                        camera.zoom_stop()
                    except AttributeError:
                        # If that fails, try the standard method
                        camera.cmd_cam_zoom_stop()
                return True
            except Exception as e:
                self.logger.error(f"Error zooming camera: {str(e)}")
        return False
            
    def _send_command(self, camera, command):
        """Send a raw VISCA command to the camera"""
        try:
            # Try different methods to send commands
            try:
                # Try using the socket directly if it exists
                if hasattr(camera, '_socket'):
                    camera._socket.send(command)
                elif hasattr(camera, 'socket'):
                    camera.socket.send(command)
                # Try using a send method if it exists
                elif hasattr(camera, 'send'):
                    camera.send(command)
                elif hasattr(camera, 'send_command'):
                    camera.send_command(command)
                else:
                    # If no method works, log an error
                    self.logger.error("No method found to send commands to camera")
                    return False
            except Exception as e:
                self.logger.error(f"Error sending command to camera: {str(e)}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error sending command to camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Stop all movement of the active camera"""
        camera = self.get_active_camera()
        if camera:
            try:
                camera.pantilt_stop()
                camera.zoom_stop()
                return True
            except Exception as e:
                self.logger.error(f"Error stopping camera: {str(e)}")
        return False
    
    def update_camera_config(self, index, name, ip, port):
        """Update camera configuration"""
        if 0 <= index < len(self.cameras):
            try:
                # Create a new camera with updated settings
                camera = Camera(ip, port)
                camera.name = name
                camera.ip = ip
                camera.port = port
                
                # Replace the old camera
                self.cameras[index] = camera
                return True
            except Exception as e:
                self.logger.error(f"Error updating camera config: {str(e)}")
        return False
    
    def store_preset(self, preset_num):
        """Store current camera position to a preset"""
        if self.active_camera_index < 0 or self.active_camera_index >= len(self.cameras):
            return False
        
        camera = self.cameras[self.active_camera_index]
        try:
            # Send VISCA command to store preset
            # Preset command format: 8x 01 04 3F 01 pp FF
            # where pp is preset number (0x00 to 0xFF)
            command = bytes([0x81, 0x01, 0x04, 0x3F, 0x01, preset_num - 1, 0xFF])
            self._send_command(camera, command)
            return True
        except Exception as e:
            print(f"Error storing preset: {e}")
            return False
    
    def recall_preset(self, preset_num):
        """Recall a stored preset position"""
        if self.active_camera_index < 0 or self.active_camera_index >= len(self.cameras):
            return False
        
        camera = self.cameras[self.active_camera_index]
        try:
            # Send VISCA command to recall preset
            # Preset recall command format: 8x 01 04 3F 02 pp FF
            # where pp is preset number (0x00 to 0xFF)
            command = bytes([0x81, 0x01, 0x04, 0x3F, 0x02, preset_num - 1, 0xFF])
            self._send_command(camera, command)
            return True
        except Exception as e:
            print(f"Error recalling preset: {e}")
            return False