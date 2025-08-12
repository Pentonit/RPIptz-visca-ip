from typing import Dict, List, Optional, Callable

try:
    import pygame
except ImportError:
    pygame = None

from .gamepad_controller import GamepadController


class ControllerManager:
    """Manages external game controllers and exposes a unified interface.
    
    Supports:
    - Game controllers via pygame (GamepadController)
    """

    def __init__(self, config: Dict):
        self._config = config
        self._active: Optional[object] = None
        self._active_type: Optional[str] = None  # "gamepad"
        self._active_gamepad_index: Optional[int] = None

    # Discovery
    def list_gamepads(self) -> List[Dict[str, str]]:
        if pygame is None:
            return []
        if not pygame.get_init():
            pygame.init()
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        result = []
        count = pygame.joystick.get_count()
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            name = j.get_name()
            result.append({"index": str(i), "name": name})
        return result

    def get_gamepad_mapping(self, fallback: Dict[str, object] = None) -> Dict[str, object]:
        mapping = (self._config.get("gamepad") or {}).get("mapping", {})
        default_map = {
            "pan_axis": 0,
            "tilt_axis": 1,
            "zoom_axis": 3,
            "invert_pan": False,
            "invert_tilt": False,
            "invert_zoom": False,
            "deadzone": 0.1,
            "buttons": {
                # action -> button index
                "zoom_in": 0,
                "zoom_out": 1,
                "stop": 2,
                "preset_store_toggle": 3,
            },
        }
        default_map.update(mapping)
        if fallback:
            default_map.update(fallback)
        return default_map

    # Activation
    def activate_gamepad(self, device_index: int, mapping: Dict[str, object]) -> None:
        self.deactivate()
        self._active = GamepadController(device_index, mapping)
        self._active_type = "gamepad"
        self._active_gamepad_index = device_index

    def deactivate(self) -> None:
        if self._active and hasattr(self._active, "stop_monitoring"):
            try:
                self._active.stop_monitoring()
            except Exception:
                pass
        self._active = None
        self._active_type = None
        self._active_gamepad_index = None

    # Unified interface
    def start_monitoring(self, callback: Callable[[float, float, float], None], button_callback: Optional[Callable[[str, bool], None]] = None) -> None:
        # Prefer first available gamepad; do not auto-activate analog
        if self._active is None and pygame is not None:
            pads = self.list_gamepads()
            if pads:
                try:
                    mapping = self.get_gamepad_mapping()
                    self.activate_gamepad(int(pads[0]["index"]), mapping)
                except Exception:
                    pass
        if self._active is not None:
            try:
                self._active.start_monitoring(callback, button_callback)
            except TypeError:
                self._active.start_monitoring(callback)

    def stop_monitoring(self) -> None:
        if self._active:
            self._active.stop_monitoring()

    def get_values(self):
        if self._active:
            return self._active.get_values()
        return 0.0, 0.0, 0.0

    # Config persistence helpers
    def set_gamepad_mapping(self, mapping: Dict[str, object]) -> None:
        self._config.setdefault("gamepad", {})["mapping"] = mapping



