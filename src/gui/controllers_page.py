from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QCheckBox, QDoubleSpinBox, QGridLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class ControllersPage(QWidget):
    """UI for selecting controllers and mapping axes/buttons."""

    def __init__(self, controller_manager, config_saver_callback):
        super().__init__()
        self.controller_manager = controller_manager
        self.config_saver_callback = config_saver_callback

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Controllers")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Gamepad selection
        gp_group = QGroupBox("Gamepad Selection")
        gp_layout = QHBoxLayout()
        self.gamepad_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.activate_gamepad_button = QPushButton("Activate Gamepad")
        self.activate_analog_button = QPushButton("Use Analog Joystick")

        self.refresh_button.clicked.connect(self._refresh_gamepads)
        self.activate_gamepad_button.clicked.connect(self._activate_selected_gamepad)
        self.activate_analog_button.clicked.connect(self._activate_analog)

        gp_layout.addWidget(QLabel("Device:"))
        gp_layout.addWidget(self.gamepad_combo)
        gp_layout.addWidget(self.refresh_button)
        gp_layout.addWidget(self.activate_gamepad_button)
        gp_layout.addWidget(self.activate_analog_button)
        gp_group.setLayout(gp_layout)
        layout.addWidget(gp_group)

        # Mapping controls
        map_group = QGroupBox("Mapping")
        map_layout = QGridLayout()

        # Axis selectors
        self.pan_axis_combo = QComboBox()
        self.tilt_axis_combo = QComboBox()
        self.zoom_axis_combo = QComboBox()
        for i in range(8):
            label = f"Axis {i}"
            self.pan_axis_combo.addItem(label, i)
            self.tilt_axis_combo.addItem(label, i)
            self.zoom_axis_combo.addItem(label, i)

        # Invert checkboxes
        self.invert_pan_cb = QCheckBox("Invert Pan")
        self.invert_tilt_cb = QCheckBox("Invert Tilt")
        self.invert_zoom_cb = QCheckBox("Invert Zoom")

        # Deadzone
        self.deadzone_spin = QDoubleSpinBox()
        self.deadzone_spin.setRange(0.0, 0.5)
        self.deadzone_spin.setSingleStep(0.01)
        self.deadzone_spin.setDecimals(2)
        self.deadzone_spin.setValue(0.10)

        # Buttons mapping (indices)
        self.zoom_in_button = QSpinBox(); self.zoom_in_button.setRange(0, 31)
        self.zoom_out_button = QSpinBox(); self.zoom_out_button.setRange(0, 31)
        self.stop_button = QSpinBox(); self.stop_button.setRange(0, 31)
        self.preset_store_toggle_button = QSpinBox(); self.preset_store_toggle_button.setRange(0, 31)

        # Apply/Save
        self.apply_button = QPushButton("Apply Mapping")
        self.apply_button.clicked.connect(self._apply_mapping)

        # Layout mapping widgets
        r = 0
        map_layout.addWidget(QLabel("Pan Axis:"), r, 0)
        map_layout.addWidget(self.pan_axis_combo, r, 1)
        map_layout.addWidget(self.invert_pan_cb, r, 2)
        r += 1
        map_layout.addWidget(QLabel("Tilt Axis:"), r, 0)
        map_layout.addWidget(self.tilt_axis_combo, r, 1)
        map_layout.addWidget(self.invert_tilt_cb, r, 2)
        r += 1
        map_layout.addWidget(QLabel("Zoom Axis:"), r, 0)
        map_layout.addWidget(self.zoom_axis_combo, r, 1)
        map_layout.addWidget(self.invert_zoom_cb, r, 2)
        r += 1
        map_layout.addWidget(QLabel("Deadzone:"), r, 0)
        map_layout.addWidget(self.deadzone_spin, r, 1)
        r += 1
        map_layout.addWidget(QLabel("Button: Zoom In"), r, 0)
        map_layout.addWidget(self.zoom_in_button, r, 1)
        r += 1
        map_layout.addWidget(QLabel("Button: Zoom Out"), r, 0)
        map_layout.addWidget(self.zoom_out_button, r, 1)
        r += 1
        map_layout.addWidget(QLabel("Button: Stop"), r, 0)
        map_layout.addWidget(self.stop_button, r, 1)
        r += 1
        map_layout.addWidget(QLabel("Button: Preset Store Toggle"), r, 0)
        map_layout.addWidget(self.preset_store_toggle_button, r, 1)
        r += 1
        map_layout.addWidget(self.apply_button, r, 0, 1, 3)

        map_group.setLayout(map_layout)
        layout.addWidget(map_group)

        layout.addStretch()

        # Live values preview
        self.live_label = QLabel("Live: pan=0.00 tilt=0.00 zoom=0.00")
        self.live_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.live_label)

        self._populate_from_config()
        self._refresh_gamepads()

        # Timer to update live values
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_live)
        self.timer.start(100)

    def _apply_mapping(self):
        mapping = self._collect_mapping()
        # Persist mapping in controller manager and save to config file
        try:
            self.controller_manager.set_gamepad_mapping(mapping)
        except Exception:
            pass
        try:
            if callable(self.config_saver_callback):
                self.config_saver_callback()
        except Exception:
            pass

    def _populate_from_config(self):
        mapping = self.controller_manager.get_gamepad_mapping()
        self.pan_axis_combo.setCurrentIndex(int(mapping.get("pan_axis", 0)))
        self.tilt_axis_combo.setCurrentIndex(int(mapping.get("tilt_axis", 1)))
        self.zoom_axis_combo.setCurrentIndex(int(mapping.get("zoom_axis", 3)))
        self.invert_pan_cb.setChecked(bool(mapping.get("invert_pan", False)))
        self.invert_tilt_cb.setChecked(bool(mapping.get("invert_tilt", False)))
        self.invert_zoom_cb.setChecked(bool(mapping.get("invert_zoom", False)))
        self.deadzone_spin.setValue(float(mapping.get("deadzone", 0.1)))
        buttons = mapping.get("buttons", {})
        self.zoom_in_button.setValue(int(buttons.get("zoom_in", 0)))
        self.zoom_out_button.setValue(int(buttons.get("zoom_out", 1)))
        self.stop_button.setValue(int(buttons.get("stop", 2)))
        self.preset_store_toggle_button.setValue(int(buttons.get("preset_store_toggle", 3)))

    def _refresh_gamepads(self):
        self.gamepad_combo.clear()
        pads = self.controller_manager.list_gamepads()
        for pad in pads:
            self.gamepad_combo.addItem(f"{pad['name']} (#{pad['index']})", int(pad["index"]))

    def _activate_selected_gamepad(self):
        if self.gamepad_combo.count() == 0:
            return
        device_index = int(self.gamepad_combo.currentData())
        mapping = self._collect_mapping()
        self.controller_manager.activate_gamepad(device_index, mapping)
        # Persist mapping
        self.controller_manager.set_gamepad_mapping(mapping)
        self.config_saver_callback()

    def _activate_analog(self):
        self.controller_manager.activate_analog()

    def _collect_mapping(self):
        return {
            "pan_axis": int(self.pan_axis_combo.currentData()),
            "tilt_axis": int(self.tilt_axis_combo.currentData()),
            "zoom_axis": int(self.zoom_axis_combo.currentData()),
            "invert_pan": bool(self.invert_pan_cb.isChecked()),
            "invert_tilt": bool(self.invert_tilt_cb.isChecked()),
            "invert_zoom": bool(self.invert_zoom_cb.isChecked()),
            "deadzone": float(self.deadzone_spin.value()),
            "buttons": {
                "zoom_in": int(self.zoom_in_button.value()),
                "zoom_out": int(self.zoom_out_button.value()),
                "stop": int(self.stop_button.value()),
                "preset_store_toggle": int(self.preset_store_toggle_button.value()),
            }
        }

    def _update_live(self):
        pan, tilt, zoom = self.controller_manager.get_values()
        self.live_label.setText(f"Live: pan={pan:.2f} tilt={tilt:.2f} zoom={zoom:.2f}")


