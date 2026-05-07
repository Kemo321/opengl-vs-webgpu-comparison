import glfw
from typing import Any, Dict, Optional
from src.core.camera import Camera
from rendercanvas.glfw import RenderCanvas as WgpuCanvas


class WindowManager:
    """Manages window creation and input handling for OpenGL and WebGPU backends.

    This class encapsulates the creation of graphics windows/canvases and handles
    keyboard and mouse input events, forwarding user input to the camera for view control.

    Attributes:
        width (int): Window width in pixels.
        height (int): Window height in pixels.
        title (str): Window title displayed in the title bar.
        camera (Camera): Camera instance for processing input-driven movement.
        keys (Dict[int, bool]): Mapping of GLFW key codes to their pressed state.
        last_x (float): Last recorded cursor x-position.
        last_y (float): Last recorded cursor y-position.
        first_mouse (bool): Flag indicating the first mouse movement event.
        window (Optional[Any]): Reference to the created window or canvas object.
        glfw_window_ptr (Optional[Any]): GLFW window pointer for common input operations.
    """

    def __init__(self, width: int, height: int, title: str, camera: Camera) -> None:
        """Initialize the WindowManager instance.

        Args:
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            title (str): Window title.
            camera (Camera): Camera instance used for input-driven movement.
        """
        self.width: int = width
        self.height: int = height
        self.title: str = title
        self.camera: Camera = camera
        self.keys: Dict[int, bool] = {}
        self.last_x: float
        self.last_y: float
        self.last_x, self.last_y = float(width) / 2.0, float(height) / 2.0
        self.first_mouse: bool = True
        self.window: Optional[Any] = None
        self.glfw_window_ptr: Optional[Any] = None

    def _key_callback(
        self, window: Any, key: int, _scancode: int, action: int, _mods: int
    ) -> None:
        """Handle GLFW key events.

        Updates the internal key state tracking and processes the escape key
        to close the window or canvas.

        Args:
            window (Any): The window that received the event.
            key (int): The keyboard key that was pressed or released.
            _scancode (int): System-specific scancode (unused).
            action (int): GLFW action code (PRESS, RELEASE, REPEAT).
            _mods (int): Bit field describing which modifier keys are held (unused).
        """
        if action == glfw.PRESS:
            self.keys[key] = True
        elif action == glfw.RELEASE:
            self.keys[key] = False

        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    def _mouse_callback(self, _window: Any, xpos: float, ypos: float) -> None:
        """Handle GLFW cursor position events.

        Computes relative mouse movement and forwards it to the camera for view control.
        The Y-axis is inverted to match typical camera control conventions.

        Args:
            _window (Any): The window that received the event (unused).
            xpos (float): Cursor x-position in screen coordinates.
            ypos (float): Cursor y-position in screen coordinates.
        """
        if self.first_mouse:
            self.last_x, self.last_y = xpos, ypos
            self.first_mouse = False

        self.camera.process_mouse_movement(xpos - self.last_x, self.last_y - ypos)
        self.last_x, self.last_y = xpos, ypos

    def init_api(self, api_type: str) -> Optional[Any]:
        """Initialize the requested graphics API and create a window or canvas.

        Configures the graphics backend (OpenGL or WebGPU) and creates the corresponding
        window or canvas object. Sets up input callbacks for both backends.

        Args:
            api_type (str): Type of graphics API to initialize. Use "opengl" for OpenGL
                or any other value to use WebGPU via wgpu.

        Returns:
            Optional[Any]: The created window or canvas object on success, None on failure.
        """
        if api_type == "opengl":
            if not glfw.init():
                return None

            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

            self.window = glfw.create_window(
                self.width, self.height, self.title, None, None
            )
            glfw.make_context_current(self.window)
            glfw.swap_interval(0)
            self.glfw_window_ptr = self.window
        else:
            if not glfw.init():
                return None
            # RenderCanvas with immediate rendering mode and vsync disabled
            self.window = WgpuCanvas(title=self.title, size=(self.width, self.height), update_mode="fastest", vsync=False)
            self.glfw_window_ptr = getattr(self.window, "_window", self.window)

        glfw.set_input_mode(self.glfw_window_ptr, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_key_callback(self.glfw_window_ptr, self._key_callback)
        glfw.set_cursor_pos_callback(self.glfw_window_ptr, self._mouse_callback)

        return self.window

    def process_input(self, delta_time: float) -> None:
        """Process keyboard input and update the camera accordingly.

        Checks the state of movement keys (W, A, S, D) and forwards the corresponding
        movement command to the camera. Movement speed is normalized using delta_time
        to ensure frame-rate independent motion.

        Args:
            delta_time (float): Time elapsed since the last frame in seconds.
        """
        if self.keys.get(glfw.KEY_W):
            self.camera.process_keyboard("FORWARD", delta_time)
        if self.keys.get(glfw.KEY_S):
            self.camera.process_keyboard("BACKWARD", delta_time)
        if self.keys.get(glfw.KEY_A):
            self.camera.process_keyboard("LEFT", delta_time)
        if self.keys.get(glfw.KEY_D):
            self.camera.process_keyboard("RIGHT", delta_time)

        if self.keys.get(glfw.KEY_LEFT):
            self.camera.process_rotation("LOOK_LEFT", delta_time)
        if self.keys.get(glfw.KEY_RIGHT):
            self.camera.process_rotation("LOOK_RIGHT", delta_time)
        if self.keys.get(glfw.KEY_UP):
            self.camera.process_rotation("LOOK_UP", delta_time)
        if self.keys.get(glfw.KEY_DOWN):
            self.camera.process_rotation("LOOK_DOWN", delta_time)
