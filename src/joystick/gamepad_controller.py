import threading
import time
from typing import Callable, Dict, Optional

try:
    import pygame
except ImportError:
    pygame = None  # Will be checked at runtime


class GamepadController:
    """Polls a single game controller using pygame and produces normalized
    pan/tilt/zoom values in the same interface as the analog JoystickController.

    The controller mapping determines which axes map to pan, tilt, and zoom,
    as well as optional axis inversion and deadzone.
    """

    def __init__(self, device_index: int, mapping: Dict[str, object], poll_interval_s: float = 0.02):
        if pygame is None:
            raise RuntimeError("pygame is not installed. Install pygame to enable gamepad support.")

        # Lazily init pygame if needed
        if not pygame.get_init():
            pygame.init()
        if not pygame.joystick.get_init():
            pygame.joystick.init()

        if device_index < 0 or device_index >= pygame.joystick.get_count():
            raise ValueError(f"Invalid gamepad device index: {device_index}")

        self._joystick = pygame.joystick.Joystick(device_index)
        self._joystick.init()

        self._mapping = {
            "pan_axis": int(mapping.get("pan_axis", 0)),
            "tilt_axis": int(mapping.get("tilt_axis", 1)),
            "zoom_axis": int(mapping.get("zoom_axis", 3)),
            "invert_pan": bool(mapping.get("invert_pan", False)),
            "invert_tilt": bool(mapping.get("invert_tilt", False)),
            "invert_zoom": bool(mapping.get("invert_zoom", False)),
            "deadzone": float(mapping.get("deadzone", 0.1)),
        }
        # Optional buttons mapping
        self._buttons_map = dict(mapping.get("buttons", {}))

        self._poll_interval_s = poll_interval_s
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[float, float, float], None]] = None
        self._button_callback: Optional[Callable[[str, bool], None]] = None

        # Last values cache for get_values()
        self._last_pan: float = 0.0
        self._last_tilt: float = 0.0
        self._last_zoom: float = 0.0

    def start_monitoring(self, callback: Callable[[float, float, float], None], button_callback: Optional[Callable[[str, bool], None]] = None) -> None:
        self._callback = callback
        self._button_callback = button_callback
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, name="GamepadControllerThread", daemon=True)
        self._thread.start()

    def stop_monitoring(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _apply_deadzone(self, value: float) -> float:
        return 0.0 if abs(value) < self._mapping["deadzone"] else value

    def _monitor_loop(self) -> None:
        while self._running:
            # Pump the event queue to keep joystick state fresh
            pygame.event.pump()

            def read_axis(axis_index: int, invert: bool) -> float:
                try:
                    v = self._joystick.get_axis(axis_index)
                except Exception:
                    v = 0.0
                if invert:
                    v = -v
                return self._apply_deadzone(v)

            pan = read_axis(self._mapping["pan_axis"], self._mapping["invert_pan"])
            tilt = read_axis(self._mapping["tilt_axis"], self._mapping["invert_tilt"])
            zoom = read_axis(self._mapping["zoom_axis"], self._mapping["invert_zoom"])

            # Cache
            self._last_pan, self._last_tilt, self._last_zoom = pan, tilt, zoom

            if self._callback:
                self._callback(pan, tilt, zoom)

            # Handle buttons
            try:
                num_buttons = self._joystick.get_numbuttons()
            except Exception:
                num_buttons = 0
            if num_buttons and self._button_callback and self._buttons_map:
                for action, btn_index in self._buttons_map.items():
                    try:
                        idx = int(btn_index)
                        if idx < 0 or idx >= num_buttons:
                            continue
                        state = self._joystick.get_button(idx)
                        prev = getattr(self, "_last_buttons", {}).get(idx, 0)
                        if state != prev:
                            if not hasattr(self, "_last_buttons"):
                                self._last_buttons = {}
                            self._last_buttons[idx] = state
                            self._button_callback(action, bool(state))
                    except Exception:
                        continue

            time.sleep(self._poll_interval_s)

    def get_values(self):
        # Ensure we poll once to keep values fresh if thread not running
        try:
            pygame.event.pump()
        except Exception:
            pass
        return self._last_pan, self._last_tilt, self._last_zoom


