import trimesh
import numpy as np
from pyglm import glm
from typing import Any, List, Sequence, Tuple, Union


class Mesh:
    """Container for mesh geometry prepared for GPU upload.

    Stores vertex positions, normals, and face indices in flattened NumPy
    arrays suitable for buffer creation.
    """

    def __init__(
        self, vertices: np.ndarray, normals: np.ndarray, indices: np.ndarray
    ) -> None:
        """Initialize mesh geometry buffers.

        Args:
            vertices: Flattened vertex positions as a float32 NumPy array.
            normals: Flattened vertex normals as a float32 NumPy array.
            indices: Flattened face indices as a uint32 NumPy array.
        """
        self.vertices: np.ndarray = vertices
        self.normals: np.ndarray = normals
        self.indices: np.ndarray = indices

    @staticmethod
    def load_from_file(filepath: str) -> "Mesh":
        """Load mesh data from a 3D model file.

        Args:
            filepath: Path to the 3D model file.

        Returns:
            Mesh: New mesh instance with flattened geometry arrays.
        """
        mesh_data = trimesh.load(filepath, force="mesh")
        vertices = np.array(mesh_data.vertices, dtype=np.float32).flatten()
        normals = np.array(mesh_data.vertex_normals, dtype=np.float32).flatten()
        indices = np.array(mesh_data.faces, dtype=np.uint32).flatten()
        return Mesh(vertices, normals, indices)


class SceneObject:
    """Renderable object definition with optional GPU instancing data."""

    def __init__(
        self,
        mesh: Mesh,
        color: Union[Tuple[float, float, float], Sequence[float]] = (0.8, 0.8, 0.8),
    ) -> None:
        """Initialize a scene object.

        Args:
            mesh: Mesh geometry assigned to this object.
            color: RGB color used as object material/albedo.

        Returns:
            None.
        """
        self.mesh: Mesh = mesh
        self.color: Any = glm.vec3(color)
        self.instance_offsets: List[Any] = [glm.vec3(0.0, 0.0, 0.0)]

    def set_instances(
        self,
        offsets: List[Union[Tuple[float, float, float], Sequence[float], Any]],
    ) -> None:
        """Set per-instance world-space offsets.

        Args:
            offsets: List of 3D position vectors for all instances.

        Returns:
            None.
        """
        self.instance_offsets = [glm.vec3(pos) for pos in offsets]


class PointLight:
    """Point light definition used by scene lighting calculations."""

    def __init__(
        self,
        position: Union[Tuple[float, float, float], Sequence[float]],
        color: Union[Tuple[float, float, float], Sequence[float]],
    ) -> None:
        """Initialize a point light.

        Args:
            position: Light position in world space.
            color: Light RGB color/intensity.

        Returns:
            None.
        """
        self.position: Any = glm.vec3(position)
        self.color: Any = glm.vec3(color)


class Scene:
    """Container for renderable objects and light sources."""

    def __init__(self) -> None:
        """Initialize an empty scene.

        Args:
            None.

        Returns:
            None.
        """
        self.objects: List[SceneObject] = []
        self.lights: List[PointLight] = []

    def add_object(self, obj: SceneObject) -> None:
        """Add a renderable object to the scene.

        Args:
            obj: Scene object instance to append.

        Returns:
            None.
        """
        self.objects.append(obj)

    def add_light(self, light: PointLight) -> None:
        """Add a point light to the scene.

        Args:
            light: Point light instance to append.

        Returns:
            None.
        """
        self.lights.append(light)

    def clear(self) -> None:
        """Remove all objects and lights from the scene.

        Args:
            None.

        Returns:
            None.
        """
        self.objects = []
        self.lights = []
