from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTabWidget, 
                            QGridLayout, QLineEdit, QSpinBox, QGroupBox,
                            QSlider, QMessageBox, QStyle, QProxyStyle, QButtonGroup, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont
from .controllers_page import ControllersPage

# Custom slider style for touch screens
class TouchSliderStyle(QProxyStyle):
    def __init__(self):
        super().__init__()
    
    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_SliderThickness:
            return 30  # Touch friendly but fits 480px height
        elif metric == QStyle.PM_SliderLength:
            return 60  # Slightly longer handle for touch
        return super().pixelMetric(metric, option, widget)

class MainWindow(QMainWindow):
    def __init__(self, camera_manager, controller_manager, config_ref, config_saver):
        super().__init__()
        
        self.camera_manager = camera_manager
        self.controller_manager = controller_manager
        self._config_ref = config_ref
        self._config_saver = config_saver
        
        # Set up the main window
        self.setWindowTitle("Camera Controller")
        self.setGeometry(0, 0, 800, 480)
        # Set window to fullscreen for 800x480 display
        self.showFullScreen()
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(6)
        # Compact margins for 800x480
        self.main_layout.setContentsMargins(6, 10, 6, 6)
        
        # Create tab widget for different screens
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        try:
            self.tab_widget.setTabBarAutoHide(False)
        except Exception:
            pass
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.control_tab = QWidget()
        self.config_tab = QWidget()
        self.presets_tab = QWidget()  # New presets tab
        self.system_tab = QWidget()  # New system tab
        self.controllers_tab = QWidget()  # New controllers tab
        
        self.tab_widget.addTab(self.control_tab, "Control")
        self.tab_widget.addTab(self.controllers_tab, "Controllers")
        self.tab_widget.addTab(self.presets_tab, "Presets")  # Add presets tab
        self.tab_widget.addTab(self.config_tab, "Config")
        self.tab_widget.addTab(self.system_tab, "System")  # Add system tab
        
        # Set up the tabs
        self.setup_control_tab()
        self.setup_presets_tab()
        self.setup_config_tab()
        self.setup_system_tab()  # Setup the new system tab
        self.setup_controllers_tab()

        # Apply a touch-friendly, high-contrast style and ensure tabs are visible
        try:
            self.apply_styles()
        except Exception:
            pass
        
        # Remove the exit button from main layout
        # self.exit_button = QPushButton("Exit")
        # self.exit_button.setMinimumHeight(25)
        # self.exit_button.setMaximumHeight(25)
        # self.exit_button.setFont(QFont("Arial", 9))
        # self.exit_button.clicked.connect(self.close)
        # self.main_layout.addWidget(self.exit_button)
        
        # Start controller monitoring with button callback (external controllers only)
        self.controller_manager.start_monitoring(self.on_joystick_movement, self.on_button_action)
        
        # Timer for updating UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms
    
    def setup_control_tab(self):
        """Set up the control tab with camera selection and controls"""
        layout = QVBoxLayout(self.control_tab)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Camera selection - replace dropdown with buttons
        camera_group = QGroupBox("Camera")
        camera_group.setFlat(True)
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(2, 2, 2, 2)
        camera_layout.setSpacing(4)
        
        # Create camera selection buttons instead of dropdown
        self.camera_buttons = []
        for i, camera_name in enumerate(self.camera_manager.get_camera_list()):
            btn = QPushButton(camera_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            btn.setFont(QFont("Arial", 11, QFont.Bold))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        controls_layout.setSpacing(6)
        
        # Left side: Joystick info and zoom slider
        left_controls = QVBoxLayout()
        left_controls.setSpacing(6)
        
        # Joystick visualization
        joystick_group = QGroupBox("Input Values")
        joystick_group.setFlat(True)
        joystick_layout = QGridLayout()
        joystick_layout.setContentsMargins(2, 2, 2, 2)
        
        self.pan_tilt_label = QLabel("Pan/Tilt: 0, 0")
        self.pan_tilt_label.setFont(QFont("Arial", 11))
        self.zoom_label = QLabel("Zoom: 0")
        self.zoom_label.setFont(QFont("Arial", 11))
        
        joystick_layout.addWidget(self.pan_tilt_label, 0, 0)
        joystick_layout.addWidget(self.zoom_label, 1, 0)
        
        joystick_group.setLayout(joystick_layout)
        left_controls.addWidget(joystick_group)
        
        # Zoom control slider - make it larger for touch
        zoom_group = QGroupBox("Zoom")
        zoom_group.setFlat(True)
        zoom_layout = QHBoxLayout()
        zoom_layout.setContentsMargins(2, 2, 2, 2)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(-100)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(0)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setMinimumHeight(40)
        
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
        
        # Zoom +/- buttons at either end of the slider
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setMinimumSize(44, 44)
        self.zoom_out_btn.setAutoRepeat(True)
        self.zoom_out_btn.setAutoRepeatInterval(120)
        self.zoom_out_btn.pressed.connect(lambda: self.camera_manager.zoom_camera(-5))
        self.zoom_out_btn.released.connect(lambda: self.camera_manager.zoom_camera(0))

        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setMinimumSize(44, 44)
        self.zoom_in_btn.setAutoRepeat(True)
        self.zoom_in_btn.setAutoRepeatInterval(120)
        self.zoom_in_btn.pressed.connect(lambda: self.camera_manager.zoom_camera(5))
        self.zoom_in_btn.released.connect(lambda: self.camera_manager.zoom_camera(0))

        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_slider, 1)
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_group.setLayout(zoom_layout)
        left_controls.addWidget(zoom_group)
        
        # Add PTZ speed control slider
        # PTZ speed segmented buttons
        speed_group = QGroupBox("PTZ Speed")
        speed_layout = QHBoxLayout()
        speed_layout.setContentsMargins(4, 4, 4, 4)
        self.speed_buttons = QButtonGroup(self)
        self.speed_map = {"Slow": 8, "Medium": 16, "Fast": 24}
        for label, val in self.speed_map.items():
            b = QPushButton(label)
            b.setCheckable(True)
            b.setMinimumHeight(44)
            b.setFont(QFont("Arial", 11))
            speed_layout.addWidget(b)
            self.speed_buttons.addButton(b, val)
        # Default Medium
        for btn in self.speed_buttons.buttons():
            if self.speed_buttons.id(btn) == 16:
                btn.setChecked(True)
                break
        speed_group.setLayout(speed_layout)
        left_controls.addWidget(speed_group)
        
        controls_layout.addLayout(left_controls, 2)  # Give left side more space
        
        # Right side: Camera control buttons
        control_group = QGroupBox("Camera Controls")
        control_layout = QGridLayout()
        control_layout.setContentsMargins(4, 4, 4, 4)
        control_layout.setSpacing(6)
        
        # Create directional buttons
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.btn_left = QPushButton("◄")
        self.btn_right = QPushButton("►")
        self.btn_stop = QPushButton("■")
        
        # Set minimum size for buttons - large for touch
        for btn in [self.btn_up, self.btn_down, self.btn_left, self.btn_right, self.btn_stop]:
            btn.setMinimumSize(70, 70)
            btn.setFont(QFont("Arial", 16))
        
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

        # Quick Presets row (Recall 1-6)
        quick_presets = QGroupBox("Quick Presets")
        qp_layout = QHBoxLayout()
        qp_layout.setContentsMargins(4, 4, 4, 4)
        self.quick_preset_buttons = []
        for i in range(6):
            pbtn = QPushButton(f"{i+1}")
            pbtn.setMinimumHeight(44)
            pbtn.setFont(QFont("Arial", 11, QFont.Bold))
            pbtn.clicked.connect(lambda checked, preset_num=i+1: self.on_quick_preset_recall(preset_num))
            qp_layout.addWidget(pbtn)
            self.quick_preset_buttons.append(pbtn)
        quick_presets.setLayout(qp_layout)
        layout.addWidget(quick_presets)
    
    def setup_presets_tab(self):
        """Set up the presets tab with preset buttons"""
        layout = QVBoxLayout(self.presets_tab)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Camera selection for presets
        camera_group = QGroupBox("Camera")
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(2, 2, 2, 2)
        camera_layout.setSpacing(4)
        
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
        self.store_mode_button.setMinimumHeight(44)
        self.store_mode_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.store_mode_button.setStyleSheet("QPushButton:checked { background-color: #ff9900; color: black; }")
        layout.addWidget(self.store_mode_button)
        
        # Preset buttons grid
        presets_group = QGroupBox("Camera Presets")
        presets_layout = QGridLayout()
        presets_layout.setSpacing(8)
        
        # Create 9 preset buttons in a 3x3 grid
        self.preset_buttons = []
        for i in range(9):
            row = i // 3
            col = i % 3
            btn = QPushButton(f"Preset {i+1}")
            btn.setMinimumSize(90, 70)
            btn.setFont(QFont("Arial", 11))
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
        
        # Camera selection for configuration (buttons instead of dropdown)
        camera_group = QGroupBox("Select Camera to Configure")
        camera_group.setFlat(True)
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(2, 2, 2, 2)
        camera_layout.setSpacing(4)
        
        self.config_camera_buttons = []
        for i, camera_name in enumerate(self.camera_manager.get_camera_list()):
            btn = QPushButton(camera_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10))
            btn.clicked.connect(lambda checked, idx=i: self.on_config_camera_button_clicked(idx))
            camera_layout.addWidget(btn)
            self.config_camera_buttons.append(btn)
        
        if self.config_camera_buttons:
            self.config_camera_buttons[0].setChecked(True)
            self.config_selected_index = 0
        else:
            self.config_selected_index = 0
        
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
        self.save_config_button.setMinimumHeight(36)
        self.save_config_button.setFont(QFont("Arial", 10))
        self.save_config_button.clicked.connect(self.on_save_config)
        layout.addWidget(self.save_config_button)
        
        # Initialize with first camera
        self.on_config_camera_selected(getattr(self, 'config_selected_index', 0))
    
    def on_config_camera_selected(self, index):
        """Handle configuration camera selection change"""
        if index >= 0 and index < len(self.camera_manager.cameras):
            camera = self.camera_manager.cameras[index]
            self.camera_name_edit.setText(camera.name)
            self.camera_ip_edit.setText(camera.ip)
            self.camera_port_edit.setValue(camera.port)
            self.config_selected_index = index

    def on_config_camera_button_clicked(self, index):
        # Update button checks
        for i, btn in enumerate(getattr(self, 'config_camera_buttons', [])):
            btn.setChecked(i == index)
        self.on_config_camera_selected(index)
    
    def on_save_config(self):
        """Save camera configuration"""
        index = getattr(self, 'config_selected_index', 0)
        name = self.camera_name_edit.text()
        ip = self.camera_ip_edit.text()
        port = self.camera_port_edit.value()
        
        if self.camera_manager.update_camera_config(index, name, ip, port):
            # Update camera button text
            if 0 <= index < len(self.camera_buttons):
                self.camera_buttons[index].setText(name)
            if hasattr(self, 'preset_camera_buttons') and 0 <= index < len(self.preset_camera_buttons):
                self.preset_camera_buttons[index].setText(name)
            if hasattr(self, 'config_camera_buttons') and 0 <= index < len(self.config_camera_buttons):
                self.config_camera_buttons[index].setText(name)
            
            # Persist to config and save file
            try:
                if 0 <= index < len(self._config_ref.get('cameras', [])):
                    self._config_ref['cameras'][index]['name'] = name
                    self._config_ref['cameras'][index]['ip'] = ip
                    self._config_ref['cameras'][index]['port'] = int(port)
                    self._config_saver()
            except Exception:
                pass
            QMessageBox.information(self, "Success", "Camera configuration saved successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save camera configuration.")
    
    def on_joystick_movement(self, x, y, zoom):
        """Handle joystick movement"""
        # Get the current speed setting
        speed = self.get_speed()
        
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
        # Get the current speed setting
        speed = self.get_speed()
        
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

    def on_button_action(self, action: str, pressed: bool):
        if action == "zoom_in":
            self.camera_manager.zoom_camera(5 if pressed else 0)
        elif action == "zoom_out":
            self.camera_manager.zoom_camera(-5 if pressed else 0)
        elif action == "stop":
            self.camera_manager.stop_camera()
        elif action == "preset_store_toggle":
            if pressed and hasattr(self, 'store_mode_button'):
                self.store_mode_button.setChecked(not self.store_mode_button.isChecked())
    
    def get_speed(self):
        """Return current PTZ speed from segmented buttons."""
        checked_id = self.speed_buttons.checkedId() if hasattr(self, 'speed_buttons') else -1
        return checked_id if checked_id > 0 else 24
    
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
        x, y, zoom = self.controller_manager.get_values()
        
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

    def closeEvent(self, event):
        # Stop controller monitoring and camera movement on close
        try:
            self.controller_manager.stop_monitoring()
        except Exception:
            pass
        try:
            self.camera_manager.stop_camera()
        except Exception:
            pass
        event.accept()

    def setup_system_tab(self):
        """Set up the system tab with exit button and other system controls"""
        layout = QVBoxLayout(self.system_tab)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Add a title label
        title_label = QLabel("System Controls")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Add exit button - make it large and centered
        self.exit_button = QPushButton("EXIT APPLICATION")
        self.exit_button.setMinimumSize(260, 80)
        self.exit_button.setFont(QFont("Arial", 14, QFont.Bold))
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

    def setup_controllers_tab(self):
        # Embed the ControllersPage widget
        self.controllers_page = ControllersPage(
            controller_manager=self.controller_manager,
            config_saver_callback=self._config_saver,
        )
        # Replace the empty tab widget with the page's layout
        tab_layout = QVBoxLayout(self.controllers_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(self.controllers_page)
    
    def on_quick_preset_recall(self, preset_num: int):
        self.camera_manager.recall_preset(preset_num)
    
    def apply_styles(self):
        # Dark, high-contrast theme suitable for touch with clearly visible tabs
        self.setStyleSheet(
            """
            QWidget { background-color: #1e1e1e; color: #f0f0f0; }
            QGroupBox { border: 1px solid #3a3a3a; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #cccccc; }
            QPushButton { background-color: #2d2d2d; border: 1px solid #555; border-radius: 8px; padding: 10px; }
            QPushButton:hover { background-color: #383838; }
            QPushButton:pressed { background-color: #444; }
            QPushButton:checked { background-color: #007acc; border-color: #007acc; color: white; }
            QTabBar::tab { background: #2d2d2d; color: #f0f0f0; padding: 10px 16px; margin: 4px; border-radius: 8px; font-size: 12px; min-height: 28px; }
            QTabBar::tab:selected { background: #007acc; color: #ffffff; }
            QTabWidget::pane { border-top: 2px solid #444; }
            QLabel { font-size: 14px; }
            QComboBox, QLineEdit, QSpinBox { background-color: #2a2a2a; border: 1px solid #555; border-radius: 6px; padding: 6px; }
            QSlider::groove:horizontal { height: 14px; background: #2a2a2a; border: 1px solid #555; border-radius: 7px; }
            QSlider::handle:horizontal { background: #007acc; border: 1px solid #007acc; width: 28px; margin: -8px 0; border-radius: 14px; }
            """
        )