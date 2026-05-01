import pytest
from src.core.camera import Camera


def test_camera_initialization():
    cam = Camera(position=(0.0, 1.0, 5.0))
    assert cam.position.x == 0.0
    assert cam.position.y == 1.0
    assert cam.position.z == 5.0


def test_camera_process_keyboard():
    cam = Camera(position=(0.0, 0.0, 0.0))
    cam.process_keyboard("FORWARD", delta_time=1.0)
    assert cam.position.z == pytest.approx(-5.0)

    cam.process_keyboard("LEFT", delta_time=1.0)
    assert cam.position.x == pytest.approx(-5.0)


def test_camera_process_mouse_movement():
    cam = Camera()
    initial_pitch = cam.pitch
    cam.process_mouse_movement(xoffset=0.0, yoffset=100.0)
    assert cam.pitch > initial_pitch


def test_camera_gimbal_lock_clamp():
    cam = Camera()
    cam.process_mouse_movement(xoffset=0.0, yoffset=10000.0)
    assert cam.pitch == 89.0

    cam.process_mouse_movement(xoffset=0.0, yoffset=-10000.0)
    assert cam.pitch == -89.0
