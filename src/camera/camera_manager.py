from visca_over_ip import Camera
import logging
import socket

class CameraManager:
    def __init__(self, camera_configs):
        self.cameras = []
        self.active_camera_index = 0
        self.logger = logging.getLogger(__name__)
        self._last_known_positions = {}  # index -> (pan, tilt, zoom)
        
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
            # Try to sync to current position of camera upon activation
            try:
                self.sync_active_camera_position()
            except Exception:
                pass
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
                # Update last known pan/tilt when moving
                try:
                    self._last_known_positions[self.active_camera_index] = (
                        self._last_known_positions.get(self.active_camera_index, (0, 0, 0))[0],
                        self._last_known_positions.get(self.active_camera_index, (0, 0, 0))[1],
                        self._last_known_positions.get(self.active_camera_index, (0, 0, 0))[2],
                    )
                except Exception:
                    pass
                return True
            except Exception as e:
                self.logger.error(f"Error moving camera: {str(e)}")
        return False
    
    def zoom_camera(self, zoom_speed):
        """Zoom the active camera with the given speed"""
        camera = self.get_active_camera()
        if camera:
            try:
                speed = max(0, min(abs(int(zoom_speed)), 7))
                if zoom_speed > 0:
                    # Zoom tele (in)
                    try:
                        try:
                            camera.zoom_tele(speed)
                        except TypeError:
                            camera.zoom_tele()
                    except AttributeError:
                        # Raw VISCA: Zoom tele variable speed: 81 01 04 07 2p FF
                        self._send_command(camera, bytes([0x81, 0x01, 0x04, 0x07, 0x20 | speed, 0xFF]))
                elif zoom_speed < 0:
                    # Zoom wide (out)
                    try:
                        try:
                            camera.zoom_wide(speed)
                        except TypeError:
                            camera.zoom_wide()
                    except AttributeError:
                        # Raw VISCA: Zoom wide variable speed: 81 01 04 07 3p FF
                        self._send_command(camera, bytes([0x81, 0x01, 0x04, 0x07, 0x30 | speed, 0xFF]))
                else:
                    # Zoom stop
                    try:
                        camera.zoom_stop()
                    except AttributeError:
                        # Raw VISCA: Zoom stop: 81 01 04 07 00 FF
                        self._send_command(camera, bytes([0x81, 0x01, 0x04, 0x07, 0x00, 0xFF]))
                return True
            except Exception as e:
                self.logger.error(f"Error zooming camera: {str(e)}")
        return False

    def _query_position(self, camera):
        """Attempt to query current pan/tilt/zoom from the camera if supported.
        Returns a tuple (pan, tilt, zoom) in whatever units the library returns,
        or None if not supported.
        """
        # Try common methods present in various libraries
        try:
            if hasattr(camera, 'get_position'):
                pos = camera.get_position()
                # Expect dict or tuple
                if isinstance(pos, dict):
                    return pos.get('pan'), pos.get('tilt'), pos.get('zoom')
                if isinstance(pos, (list, tuple)) and len(pos) >= 3:
                    return pos[0], pos[1], pos[2]
        except Exception:
            pass
        # Raw VISCA inquiry could be implemented here if needed
        return None

    def sync_active_camera_position(self):
        """Fetch current camera position and store as last known so UI starts at that state."""
        camera = self.get_active_camera()
        if not camera:
            return False
        pos = self._query_position(camera)
        if pos is not None:
            self._last_known_positions[self.active_camera_index] = pos
            return True
        return False
            
    def _send_command(self, camera, command):
        """Send a raw VISCA command to the camera"""
        # Preferred: send via UDP directly to the camera IP/port to avoid relying on private API
        try:
            ip = getattr(camera, 'ip', None)
            port = getattr(camera, 'port', None)
            if ip and port:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(0.5)
                    s.sendto(command, (ip, int(port)))
                return True
        except Exception as e:
            self.logger.error(f"UDP send failed: {e}")
        # Fallback: try library internals
        try:
            if hasattr(camera, '_socket'):
                camera._socket.send(command)
                return True
            if hasattr(camera, 'socket'):
                camera.socket.send(command)
                return True
            if hasattr(camera, 'send'):
                camera.send(command)
                return True
            if hasattr(camera, 'send_command'):
                camera.send_command(command)
                return True
            self.logger.error("No method found to send commands to camera")
            return False
        except Exception as e:
            self.logger.error(f"Error sending command to camera via fallback: {str(e)}")
            return False
    
    def stop_camera(self):
        """Stop all movement of the active camera"""
        camera = self.get_active_camera()
        if camera:
            try:
                # Prefer pantilt(0,0) which most libs treat as stop
                try:
                    camera.pantilt(0, 0)
                except AttributeError:
                    # Raw VISCA: PanTilt stop (vv=00 ww=00, dir codes 03 03)
                    self._send_command(camera, bytes([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x03, 0xFF]))

                try:
                    camera.zoom_stop()
                except AttributeError:
                    # Raw VISCA: Zoom stop
                    self._send_command(camera, bytes([0x81, 0x01, 0x04, 0x07, 0x00, 0xFF]))
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
            # Try with 1-based first (common), then 0-based
            for code in (preset_num, preset_num - 1):
                try:
                    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x01, max(0, code) & 0xFF, 0xFF])
                    if self._send_command(camera, command):
                        return True
                except Exception:
                    pass
            return False
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
            # Try with 1-based first (common), then 0-based
            for code in (preset_num, preset_num - 1):
                try:
                    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x02, max(0, code) & 0xFF, 0xFF])
                    if self._send_command(camera, command):
                        return True
                except Exception:
                    pass
            return False
        except Exception as e:
            print(f"Error recalling preset: {e}")
            return False