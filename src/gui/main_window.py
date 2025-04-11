from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTabWidget, 
                            QGridLayout, QLineEdit, QSpinBox, QGroupBox,
                            QSlider, QMessageBox, QStyle, QProxyStyle)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont

# Custom slider style for touch screens
class TouchSliderStyle(QProxyStyle):
    def __init__(self):
        super().__init__()
    
    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_SliderThickness:
            return 50  # Make the slider thicker
        elif metric == QStyle.PM_SliderLength:
            return 80  # Make the handle much longer
        elif metric == QStyle.PM_SliderControlThickness:
            return 50  # Make the handle thicker
        return super().pixelMetric(metric, option, widget)

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
        self.main_layout.setSpacing(2)  # Further reduce spacing
        self.main_layout.setContentsMargins(2, 2, 2, 2)  # Further reduce margins
        
        # Create tab widget for different screens
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.control_tab = QWidget()
        self.config_tab = QWidget()
        self.presets_tab = QWidget()  # New presets tab
        self.system_tab = QWidget()  # New system tab
        
        self.tab_widget.addTab(self.control_tab, "Control")
        self.tab_widget.addTab(self.presets_tab, "Presets")  # Add presets tab
        self.tab_widget.addTab(self.config_tab, "Configuration")
        self.tab_widget.addTab(self.system_tab, "System")  # Add system tab
        
        # Set up the tabs
        self.setup_control_tab()
        self.setup_presets_tab()
        self.setup_config_tab()
        self.setup_system_tab()  # Setup the new system tab
        
        # Remove the exit button from main layout
        # self.exit_button = QPushButton("Exit")
        # self.exit_button.setMinimumHeight(25)
        # self.exit_button.setMaximumHeight(25)
        # self.exit_button.setFont(QFont("Arial", 9))
        # self.exit_button.clicked.connect(self.close)
        # self.main_layout.addWidget(self.exit_button)
        
        # Start joystick monitoring
        self.joystick_controller.start_monitoring(self.on_joystick_movement)
        
        # Timer for updating UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms
    
    def setup_control_tab(self):
        """Set up the control tab with camera selection and controls"""
        layout = QVBoxLayout(self.control_tab)
        layout.setSpacing(2)  # Further reduce spacing
        layout.setContentsMargins(2, 2, 2, 2)  # Further reduce margins
        
        # Camera selection - replace dropdown with buttons
        camera_group = QGroupBox("Camera Selection")
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        
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
        
        # Create a horizontal layout for joystick info and camera controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        
        # Left side: Joystick info and zoom slider
        left_controls = QVBoxLayout()
        left_controls.setSpacing(2)
        
        # Joystick visualization
        joystick_group = QGroupBox("Joystick Control")
        joystick_layout = QGridLayout()
        joystick_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        
        self.pan_tilt_label = QLabel("Pan/Tilt: 0, 0")
        self.pan_tilt_label.setFont(QFont("Arial", 10))
        self.zoom_label = QLabel("Zoom: 0")
        self.zoom_label.setFont(QFont("Arial", 10))
        
        joystick_layout.addWidget(self.pan_tilt_label, 0, 0)
        joystick_layout.addWidget(self.zoom_label, 1, 0)
        
        joystick_group.setLayout(joystick_layout)
        left_controls.addWidget(joystick_group)
        
        # Zoom control slider - make it larger for touch
        zoom_group = QGroupBox("Zoom Control")
        zoom_layout = QVBoxLayout()
        zoom_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(-100)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(0)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setMinimumHeight(70)  # Make slider even taller
        
        # Apply the touch-friendly style
        touch_style = TouchSliderStyle()
        self.zoom_slider.setStyle(touch_style)
        
        # Make the slider more visible with a border
        self.zoom_slider.setStyleSheet("""
            QSlider {
                border: 2px solid #5c5c5c;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)
        
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        
        zoom_layout.addWidget(self.zoom_slider)
        zoom_group.setLayout(zoom_layout)
        left_controls.addWidget(zoom_group)
        
        # Add PTZ speed control slider
        speed_group = QGroupBox("PTZ Speed")
        speed_layout = QVBoxLayout()
        speed_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(24)  # VISCA max speed is 24
        self.speed_slider.setValue(12)  # Default to middle speed
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(4)
        self.speed_slider.setMinimumHeight(70)  # Make slider even taller
        
        # Apply the touch-friendly style
        self.speed_slider.setStyle(TouchSliderStyle())
        
        # Make the slider more visible with a border
        self.speed_slider.setStyleSheet("""
            QSlider {
                border: 2px solid #5c5c5c;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)
        
        self.speed_slider.valueChanged.connect(self.on_speed_slider_changed)
        
        self.speed_label = QLabel(f"Speed: {self.speed_slider.value()}")
        self.speed_label.setFont(QFont("Arial", 10))
        self.speed_label.setAlignment(Qt.AlignCenter)
        
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_group.setLayout(speed_layout)
        left_controls.addWidget(speed_group)
        
        controls_layout.addLayout(left_controls, 2)  # Give left side more space
        
        # Right side: Camera control buttons
        control_group = QGroupBox("Camera Controls")
        control_layout = QGridLayout()
        control_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        control_layout.setSpacing(2)  # Reduce spacing
        
        # Create directional buttons
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.btn_left = QPushButton("◄")
        self.btn_right = QPushButton("►")
        self.btn_stop = QPushButton("■")
        
        # Set minimum size for buttons - make them smaller
        for btn in [self.btn_up, self.btn_down, self.btn_left, self.btn_right, self.btn_stop]:
            btn.setMinimumSize(50, 50)  # Further reduced from 60x60
            btn.setMaximumSize(50, 50)  # Add maximum size
            btn.setFont(QFont("Arial", 12))  # Reduced from 14
        
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
        controls_layout.addWidget(control_group, 1)  # Give right side less space
        
        layout.addLayout(controls_layout)
    
    def setup_presets_tab(self):
        """Set up the presets tab with preset buttons"""
        layout = QVBoxLayout(self.presets_tab)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Camera selection for presets
        camera_group = QGroupBox("Camera")
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create camera selection buttons for presets tab
        self.preset_camera_buttons = []
        for i, camera_name in enumerate(self.camera_manager.get_camera_list()):
            btn = QPushButton(camera_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10))
            # Use a lambda with default argument to capture the correct index
            btn.clicked.connect(lambda checked, idx=i: self.on_preset_camera_clicked(idx))
            camera_layout.addWidget(btn)
            self.preset_camera_buttons.append(btn)
        
        # Set the first camera as active
        if self.preset_camera_buttons:
            self.preset_camera_buttons[0].setChecked(True)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Store button
        self.store_mode_button = QPushButton("STORE MODE")
        self.store_mode_button.setCheckable(True)
        self.store_mode_button.setMinimumHeight(50)
        self.store_mode_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.store_mode_button.setStyleSheet("QPushButton:checked { background-color: #ff9900; color: black; }")
        layout.addWidget(self.store_mode_button)
        
        # Preset buttons grid
        presets_group = QGroupBox("Camera Presets")
        presets_layout = QGridLayout()
        presets_layout.setSpacing(10)
        
        # Create 9 preset buttons in a 3x3 grid
        self.preset_buttons = []
        for i in range(9):
            row = i // 3
            col = i % 3
            btn = QPushButton(f"Preset {i+1}")
            btn.setMinimumSize(100, 80)
            btn.setFont(QFont("Arial", 12))
            # Connect to preset handler with the preset number
            btn.clicked.connect(lambda checked, preset_num=i+1: self.on_preset_button(preset_num))
            presets_layout.addWidget(btn, row, col)
            self.preset_buttons.append(btn)
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
    
    def on_preset_camera_clicked(self, index):
        """Handle camera selection in presets tab"""
        # Update button states
        for i, btn in enumerate(self.preset_camera_buttons):
            btn.setChecked(i == index)
        
        # Update camera buttons in control tab to match
        for i, btn in enumerate(self.camera_buttons):
            btn.setChecked(i == index)
        
        # Set the active camera
        self.camera_manager.set_active_camera(index)
    
    def on_preset_button(self, preset_num):
        """Handle preset button press"""
        if self.store_mode_button.isChecked():
            # Store current position to this preset
            success = self.camera_manager.store_preset(preset_num)
            if success:
                self.preset_buttons[preset_num-1].setText(f"Preset {preset_num} ✓")
                self.store_mode_button.setChecked(False)  # Turn off store mode after storing
                QMessageBox.information(self, "Success", f"Position stored to Preset {preset_num}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to store Preset {preset_num}")
        else:
            # Recall this preset
            success = self.camera_manager.recall_preset(preset_num)
            if not success:
                QMessageBox.warning(self, "Error", f"Failed to recall Preset {preset_num}")
    
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
        self.config_camera_selector.setFont(QFont("Arial", 10))
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
        self.save_config_button.setMinimumHeight(40)
        self.save_config_button.setFont(QFont("Arial", 10))
        self.save_config_button.clicked.connect(self.on_save_config)
        layout.addWidget(self.save_config_button)
        
        # Initialize with first camera
        self.on_config_camera_selected(0)
    
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
        # Get the current speed setting from the slider
        speed = self.speed_slider.value() if hasattr(self, 'speed_slider') else 24
        
        # Scale values to appropriate ranges for camera control
        pan_speed = int(x * speed)  # Use the speed setting
        tilt_speed = int(-y * speed)  # Use the speed setting
        zoom_speed = int(zoom * 7)  # VISCA zoom speed range: 0 to 7
        
        # Move camera
        if pan_speed != 0 or tilt_speed != 0:
            self.camera_manager.move_camera(pan_speed, tilt_speed)
        
        # Zoom camera
        if zoom_speed != 0:
            self.camera_manager.zoom_camera(zoom_speed)
    
    def on_speed_slider_changed(self, value):
        """Handle speed slider change"""
        self.speed_label.setText(f"Speed: {value}")
        # The actual speed will be used in the direction button handlers
    
    def on_direction_button(self, pan, tilt):
        """Handle direction button press/release"""
        # Get the current speed setting from the slider
        speed = self.speed_slider.value() if hasattr(self, 'speed_slider') else 24
        
        # Scale to appropriate ranges for camera control using the speed setting
        pan_speed = int(pan * speed)  # VISCA pan speed range: -24 to 24
        tilt_speed = int(tilt * speed)  # VISCA tilt speed range: -24 to 24
        
        # Move camera
        self.camera_manager.move_camera(pan_speed, tilt_speed)
    
    def on_stop_button(self):
        """Handle stop button press"""
        self.camera_manager.stop_camera()
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change"""
        zoom_speed = int(value / 14)  # Scale to VISCA zoom speed range
        self.camera_manager.zoom_camera(zoom_speed)
    
    def on_camera_button_clicked(self, index):
        """Handle camera selection in control tab"""
        # Update button states
        for i, btn in enumerate(self.camera_buttons):
            btn.setChecked(i == index)
        
        # Update camera buttons in presets tab to match
        for i, btn in enumerate(self.preset_camera_buttons):
            btn.setChecked(i == index)
        
        # Set the active camera
        self.camera_manager.set_active_camera(index)
    
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

    def setup_system_tab(self):
        """Set up the system tab with exit button and other system controls"""
        layout = QVBoxLayout(self.system_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add a title label
        title_label = QLabel("System Controls")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Add exit button - make it large and centered
        self.exit_button = QPushButton("EXIT APPLICATION")
        self.exit_button.setMinimumSize(300, 100)
        self.exit_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
        """)
        self.exit_button.clicked.connect(self.close)
        
        # Create a horizontal layout to center the exit button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()  # Push everything to the top