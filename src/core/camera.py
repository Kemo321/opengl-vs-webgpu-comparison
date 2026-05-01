from typing import Tuple
import glm


class Camera:
    """
    Perspective camera with 6 degrees of freedom for movement and rotation.

    Implements a free-flight control scheme (FPS-style) using Euler angles
    (yaw and pitch) for rotation and keyboard input for movement in all directions.
    """

    def __init__(
        self,
        position: Tuple[float, float, float] = (0.0, 0.0, 5.0),
        aspect_ratio: float = 16 / 9,
    ) -> None:
        """
        Initialize the camera with a position and aspect ratio.

        Args:
            position: Initial camera position in world space (default: [0, 0, 5]).
            aspect_ratio: View aspect ratio used for the projection matrix (default: 16/9).
        """
        self.position: glm.vec3 = glm.vec3(position)
        self.front: glm.vec3 = glm.vec3(0.0, 0.0, -1.0)
        self.up: glm.vec3 = glm.vec3(0.0, 1.0, 0.0)
        self.right: glm.vec3 = glm.vec3(1.0, 0.0, 0.0)
        self.world_up: glm.vec3 = glm.vec3(0.0, 1.0, 0.0)

        self.yaw: float = -90.0
        self.pitch: float = 0.0

        self.movement_speed: float = 5.0
        self.mouse_sensitivity: float = 0.1

        self.fov: float = glm.radians(45.0)
        self.aspect_ratio: float = aspect_ratio

        self._update_camera_vectors()

    def get_view_matrix(self) -> glm.mat4:
        """
        Generate the view matrix from current camera position and orientation.

        Returns:
            A 4x4 view matrix for transforming world coordinates to camera space.
        """
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_projection_matrix(self) -> glm.mat4:
        """
        Generate the perspective projection matrix.

        Returns:
            A 4x4 projection matrix with near plane at 0.1 and far plane at 1000.0.
        """
        return glm.perspective(self.fov, self.aspect_ratio, 0.1, 1000.0)

    def process_keyboard(self, direction: str, delta_time: float):
        """
        Update camera position based on keyboard input.

        Args:
            direction: Movement direction ("FORWARD", "BACKWARD", "LEFT", "RIGHT")
            delta_time: Time elapsed since last frame in seconds
        """
        # Calculate the distance to move based on speed and frame time
        velocity = self.movement_speed * delta_time

        # Update position relative to the camera orientation
        if direction == "FORWARD":
            self.position += self.front * velocity
        elif direction == "BACKWARD":
            self.position -= self.front * velocity
        elif direction == "LEFT":
            self.position -= self.right * velocity
        elif direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset: float, yoffset: float):
        """
        Update camera rotation based on mouse movement.

        Args:
            xoffset: Horizontal mouse movement in pixels
            yoffset: Vertical mouse movement in pixels
        """
        # Apply mouse sensitivity scaling
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        # Update rotation angles
        self.yaw += xoffset
        self.pitch += yoffset

        # Clamp pitch to prevent camera flip (gimbal lock)
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Recalculate direction vectors from the new angles
        self._update_camera_vectors()

    def _update_camera_vectors(self):
        """
        Recalculate camera direction vectors from the current Euler angles.

        Updates the front, right, and up vectors based on yaw and pitch angles.
        All resulting vectors are normalized to unit length.
        """
        # Calculate the new front vector using spherical coordinates
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))

        # Normalize and store the front vector
        self.front = glm.normalize(front)

        # Recalculate the right vector as perpendicular to front and world up
        self.right = glm.normalize(glm.cross(self.front, self.world_up))

        # Recalculate the up vector as perpendicular to right and front vectors
        self.up = glm.normalize(glm.cross(self.right, self.front))
