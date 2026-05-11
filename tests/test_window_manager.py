import pytest
import glfw
from src.core.window_manager import WindowManager
from src.core.camera import Camera


def test_window_manager_init_opengl(monkeypatch):
    monkeypatch.setattr(glfw, 'init', lambda: True)
    monkeypatch.setattr(glfw, 'window_hint', lambda *args, **kwargs: None)
    monkeypatch.setattr(glfw, 'create_window', lambda *args, **kwargs: "MOCK_WINDOW_PTR")
    monkeypatch.setattr(glfw, 'make_context_current', lambda *args, **kwargs: None)
    monkeypatch.setattr(glfw, 'swap_interval', lambda *args, **kwargs: None)
    monkeypatch.setattr(glfw, 'set_input_mode', lambda *args, **kwargs: None)
    monkeypatch.setattr(glfw, 'set_key_callback', lambda *args, **kwargs: None)
    monkeypatch.setattr(glfw, 'set_cursor_pos_callback', lambda *args, **kwargs: None)

    cam = Camera()
    wm = WindowManager(800, 600, "Test", cam)

    window = wm.init_api("opengl")
    assert window == "MOCK_WINDOW_PTR"
    assert wm.glfw_window_ptr == "MOCK_WINDOW_PTR"


def test_window_manager_process_input():
    cam = Camera(position=(0, 0, 0))
    wm = WindowManager(800, 600, "Test", cam)
    wm.glfw_window_ptr = "MOCK_WINDOW"

    wm.keys[glfw.KEY_W] = True

    wm.process_input(delta_time=1.0)
    assert cam.position.z == pytest.approx(-5.0)
