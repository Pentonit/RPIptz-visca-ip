from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTabWidget, 
                            QGridLayout, QLineEdit, QSpinBox, QGroupBox,
                            QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self, camera_manager, joystick_controller):
        super().__init__()
        
        self.camera_manager = camera_manager
        self.joystick_controller = joystick_controller
        
        # Set up the main window
        self.setWindowTitle("Camera Controller")
        self.setGeometry(0, 0, 800, 480)
        # Set window to fullscreen for 800x480 display
        self.showFullScreen()
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(3)  # Further reduce spacing
        self.main_layout.setContentsMargins(3, 3, 3, 3)  # Further reduce margins
        
        # Create tab widget for different screens
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.control_tab = QWidget()
        self.config_tab = QWidget()
        
        self.tab_widget.addTab(self.control_tab, "Control")
        self.tab_widget.addTab(self.config_tab, "Configuration")
        
        # Set up the control tab
        self.setup_control_tab()
        
        # Set up the configuration tab
        self.setup_config_tab()
        
        # Add exit button at the bottom - make it smaller
        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumHeight(30)  # Further reduced from 40
        self.exit_button.setMaximumHeight(30)  # Add maximum height
        self.exit_button.setFont(QFont("Arial", 10))  # Reduced from 12
        self.exit_button.clicked.connect(self.close)
        self.main_layout.addWidget(self.exit_button)
        
        # Start joystick monitoring
        self.joystick_controller.start_monitoring(self.on_joystick_movement)
        
        # Timer for updating UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms
    
    def setup_control_tab(self):
        """Set up the control tab with camera selection and controls"""
        layout = QVBoxLayout(self.control_tab)
        layout.setSpacing(3)  # Further reduce spacing
        layout.setContentsMargins(3, 3, 3, 3)  # Further reduce margins
        
        # Camera selection - replace dropdown with buttons
        camera_group = QGroupBox("Camera Selection")
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(3, 3, 3, 3)  # Reduce margins
        
        # Create camera selection buttons instead of dropdown
        self.camera_buttons = []
        for i, camera_name in enumerate(self.camera_manager.get_camera_list()):
            btn = QPushButton(camera_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)  # Make buttons taller for touch
            btn.setFont(QFont("Arial", 10))
            # Use a lambda with default argument to capture the correct index
            btn.clicked.connect(lambda checked, idx=i: self.on_camera_button_clicked(idx))
            camera_layout.addWidget(btn)
            self.camera_buttons.append(btn)
        
        # Set the first camera as active
        if self.camera_buttons:
            self.camera_buttons[0].setChecked(True)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Joystick visualization
        joystick_group = QGroupBox("Joystick Control")
        joystick_layout = QGridLayout()
        joystick_layout.setContentsMargins(3, 3, 3, 3)  # Reduce margins
        
        self.pan_tilt_label = QLabel("Pan/Tilt: 0, 0")
        self.pan_tilt_label.setFont(QFont("Arial", 10))
        self.zoom_label = QLabel("Zoom: 0")
        self.zoom_label.setFont(QFont("Arial", 10))
        
        joystick_layout.addWidget(self.pan_tilt_label, 0, 0)
        joystick_layout.addWidget(self.zoom_label, 1, 0)
        
        joystick_group.setLayout(joystick_layout)
        layout.addWidget(joystick_group)
        
        # Zoom control slider - make it larger for touch
        zoom_group = QGroupBox("Zoom Control")
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(3, 3, 3, 3)  # Reduce margins
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(-100)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(0)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setMinimumHeight(50)  # Make slider taller
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        
        zoom_layout.addWidget(self.zoom_slider)
        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)
        
        # Camera control buttons
        control_group = QGroupBox("Camera Controls")
        control_layout = QGridLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        control_layout.setSpacing(5)  # Reduce spacing
        
        # Create directional buttons
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.btn_left = QPushButton("◄")
        self.btn_right = QPushButton("►")
        self.btn_stop = QPushButton("■")
        
        # Set minimum size for buttons to make them touch-friendly but smaller
        for btn in [self.btn_up, self.btn_down, self.btn_left, self.btn_right, self.btn_stop]:
            btn.setMinimumSize(60, 60)  # Reduced from 80x80
            btn.setFont(QFont("Arial", 14))  # Reduced from 16
        
        # Connect button signals
        self.btn_up.pressed.connect(lambda: self.on_direction_button(0, -1))
        self.btn_up.released.connect(lambda: self.on_direction_button(0, 0))
        
        self.btn_down.pressed.connect(lambda: self.on_direction_button(0, 1))
        self.btn_down.released.connect(lambda: self.on_direction_button(0, 0))
        
        self.btn_left.pressed.connect(lambda: self.on_direction_button(-1, 0))
        self.btn_left.released.connect(lambda: self.on_direction_button(0, 0))
        
        self.btn_right.pressed.connect(lambda: self.on_direction_button(1, 0))
        self.btn_right.released.connect(lambda: self.on_direction_button(0, 0))
        
        self.btn_stop.clicked.connect(self.on_stop_button)
        
        # Add buttons to layout
        control_layout.addWidget(self.btn_up, 0, 1)
        control_layout.addWidget(self.btn_left, 1, 0)
        control_layout.addWidget(self.btn_stop, 1, 1)
        control_layout.addWidget(self.btn_right, 1, 2)
        control_layout.addWidget(self.btn_down, 2, 1)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
    
    def setup_config_tab(self):
        """Set up the configuration tab with camera settings"""
        layout = QVBoxLayout(self.config_tab)
        layout.setSpacing(5)  # Reduce spacing
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Camera selection for configuration
        camera_group = QGroupBox("Select Camera to Configure")
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        self.config_camera_selector = QComboBox()
        self.config_camera_selector.addItems(self.camera_manager.get_camera_list())
        self.config_camera_selector.setFont(QFont("Arial", 10))  # Reduced from 12
        self.config_camera_selector.currentIndexChanged.connect(self.on_config_camera_selected)
        
        camera_layout.addWidget(QLabel("Camera:"))
        camera_layout.addWidget(self.config_camera_selector)
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Camera configuration fields
        config_group = QGroupBox("Camera Configuration")
        config_layout = QGridLayout()
        config_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Name field
        config_layout.addWidget(QLabel("Name:"), 0, 0)
        self.camera_name_edit = QLineEdit()
        config_layout.addWidget(self.camera_name_edit, 0, 1)
        
        # IP Address field
        config_layout.addWidget(QLabel("IP Address:"), 1, 0)
        self.camera_ip_edit = QLineEdit()
        config_layout.addWidget(self.camera_ip_edit, 1, 1)
        
        # Port field
        config_layout.addWidget(QLabel("Port:"), 2, 0)
        self.camera_port_edit = QSpinBox()
        self.camera_port_edit.setMinimum(1)
        self.camera_port_edit.setMaximum(65535)
        self.camera_port_edit.setValue(52381)  # Default VISCA port
        config_layout.addWidget(self.camera_port_edit, 2, 1)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Save button
        self.save_config_button = QPushButton("Save Configuration")
        self.save_config_button.setMinimumHeight(40)  # Reduced from 50
        self.save_config_button.setFont(QFont("Arial", 10))  # Reduced from 12
        self.save_config_button.clicked.connect(self.on_save_config)
        layout.addWidget(self.save_config_button)
        
        # Initialize with first camera
        self.on_config_camera_selected(0)
    
    def on_camera_button_clicked(self, index):
        """Handle camera selection button click"""
        # Update button states
        for i, btn in enumerate(self.camera_buttons):
            btn.setChecked(i == index)
        
        # Set the active camera
        self.camera_manager.set_active_camera(index)
    
    def on_config_camera_selected(self, index):
        """Handle configuration camera selection change"""
        if index >= 0 and index < len(self.camera_manager.cameras):
            camera = self.camera_manager.cameras[index]
            self.camera_name_edit.setText(camera.name)
            self.camera_ip_edit.setText(camera.ip)
            self.camera_port_edit.setValue(camera.port)
    
    def on_save_config(self):
        """Save camera configuration"""
        index = self.config_camera_selector.currentIndex()
        name = self.camera_name_edit.text()
        ip = self.camera_ip_edit.text()
        port = self.camera_port_edit.value()
        
        if self.camera_manager.update_camera_config(index, name, ip, port):
            # Update camera button text
            if 0 <= index < len(self.camera_buttons):
                self.camera_buttons[index].setText(name)
            
            # Update config dropdown
            self.config_camera_selector.clear()
            self.config_camera_selector.addItems(self.camera_manager.get_camera_list())
            
            QMessageBox.information(self, "Success", "Camera configuration saved successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save camera configuration.")
    
    def on_joystick_movement(self, x, y, zoom):
        """Handle joystick movement"""
        # Scale values to appropriate ranges for camera control
        pan_speed = int(x * 24)  # VISCA pan speed range: -24 to 24
        tilt_speed = int(-y * 24)  # VISCA tilt speed range: -24 to 24
        zoom_speed = int(zoom * 7)  # VISCA zoom speed range: 0 to 7
        
        # Move camera
        if pan_speed != 0 or tilt_speed != 0:
            self.camera_manager.move_camera(pan_speed, tilt_speed)
        
        # Zoom camera
        if zoom_speed != 0:
            self.camera_manager.zoom_camera(zoom_speed)
    
    def on_direction_button(self, pan, tilt):
        """Handle direction button press/release"""
        # Scale to appropriate ranges for camera control
        pan_speed = int(pan * 24)  # VISCA pan speed range: -24 to 24
        tilt_speed = int(tilt * 24)  # VISCA tilt speed range: -24 to 24
        
        # Move camera
        self.camera_manager.move_camera(pan_speed, tilt_speed)
    
    def on_stop_button(self):
        """Handle stop button press"""
        self.camera_manager.stop_camera()
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change"""
        zoom_speed = int(value / 14)  # Scale to VISCA zoom speed range
        self.camera_manager.zoom_camera(zoom_speed)
    
    def update_ui(self):
        """Update UI elements with current values"""
        # Get joystick values
        x, y, zoom = self.joystick_controller.get_values()
        
        # Update labels
        self.pan_tilt_label.setText(f"Pan/Tilt: {x:.2f}, {y:.2f}")
        self.zoom_label.setText(f"Zoom: {zoom:.2f}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Exit fullscreen mode with Escape key
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        super().keyPressEvent(event)
        
        # Stop joystick monitoring
        self.joystick_controller.stop_monitoring()
        
        # Stop camera movements
        self.camera_manager.stop_camera()
        
        # Accept the close event
        event.accept()