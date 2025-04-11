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
                    camera.zoom_tele(abs(zoom_speed))
                elif zoom_speed < 0:
                    camera.zoom_wide(abs(zoom_speed))
                else:
                    camera.zoom_stop()
                return True
            except Exception as e:
                self.logger.error(f"Error zooming camera: {str(e)}")
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