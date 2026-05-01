import pytest
from src.core.window_manager import WindowManager
from src.core.camera import Camera


def test_window_manager_init_opengl(mocker):
    mocker.patch('glfw.init', return_value=True)
    mocker.patch('glfw.window_hint')
    mocker.patch('glfw.create_window', return_value="MOCK_WINDOW_PTR")
    mocker.patch('glfw.make_context_current')
    mocker.patch('glfw.swap_interval')
    mocker.patch('glfw.set_input_mode')
    mocker.patch('glfw.set_key_callback')
    mocker.patch('glfw.set_cursor_pos_callback')

    cam = Camera()
    wm = WindowManager(800, 600, "Test", cam)

    window = wm.init_api("opengl")
    assert window == "MOCK_WINDOW_PTR"
    assert wm.glfw_window_ptr == "MOCK_WINDOW_PTR"


def test_window_manager_process_input(mocker):
    cam = Camera(position=(0, 0, 0))
    wm = WindowManager(800, 600, "Test", cam)
    wm.glfw_window_ptr = "MOCK_WINDOW"

    import glfw

    wm.keys[glfw.KEY_W] = True

    wm.process_input(delta_time=1.0)
    assert cam.position.z == pytest.approx(-5.0)
