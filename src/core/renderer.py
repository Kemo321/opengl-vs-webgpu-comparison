from abc import ABC, abstractmethod
from typing import Any


class Renderer(ABC):
    """Abstract base class for graphics API renderers.

    Implementations (for example: OpenGL, WebGPU) must provide concrete
    implementations for context initialization, per-frame rendering and
    resource cleanup.

    All methods are intentionally minimal and focus on the contract rather
    than implementation details.
    """

    @abstractmethod
    def init_context(self, window: Any) -> None:
        """Initialize the graphics rendering context.

        Args:
            window: Target window or surface where rendering will occur.

        Returns:
            None
        """
        raise NotImplementedError()

    @abstractmethod
    def render_frame(
        self, scene: Any, camera: Any, use_instancing: bool = True
    ) -> None:
        """Render a single frame using provided scene and camera data.

        Args:
            scene: Scene data container (geometry, materials, lights, etc.).
            camera: Camera describing view and projection parameters.
            use_instancing: Flag to enable or disable instancing.

        Returns:
            None
        """
        raise NotImplementedError()

    @abstractmethod
    def cleanup(self) -> None:
        """Release GPU and renderer resources.

        Implementations must free textures, buffers and other GPU-related
        resources to avoid leaks prior to application shutdown.

        Returns:
            None
        """
        raise NotImplementedError()
