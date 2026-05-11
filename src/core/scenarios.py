import sys
from typing import List

import numpy as np

from src.core.scene import Scene, SceneObject, Mesh, PointLight


def _add_default_lights(scene: Scene) -> None:
    """Add two default point lights to a scene.

    These lights are used to preserve API consistency across renderers.

    Args:
        scene (Scene): The scene to which default lights will be added.

    Returns:
        None
    """
    # Warm key light
    scene.add_light(PointLight(position=(0, 10, 5), color=(1.0, 0.9, 0.8)))
    # Cold fill light
    scene.add_light(PointLight(position=(0, -10, -20), color=(0.2, 0.2, 0.8)))


def setup_complex_object_scenario(scene: Scene) -> None:
    """Configure the scene with three instanced model displays.

    Loads three model files, creates a single instance for each object, and
    attaches two default lights.

    Args:
        scene (Scene): The scene to configure.

    Returns:
        None
    """
    scene.clear()

    try:
        lucy_mesh = Mesh.load_from_file("assets/lucy.obj")
        dragon_mesh = Mesh.load_from_file("assets/xyzrgb_dragon.obj")
        statuette_mesh = Mesh.load_from_file("assets/xyzrgb_statuette.obj")
    except Exception as exc:
        print(f"Error loading models: {exc}")
        sys.exit(1)

    try:
        lucy = SceneObject(lucy_mesh, color=(0.8, 0.8, 0.9))
        lucy.set_instances([[-0.0, -0.0, -1000.0]])
        scene.add_object(lucy)

        dragon = SceneObject(dragon_mesh, color=(0.2, 0.8, 0.3))
        dragon.set_instances([[-300.0, 0.0, -500.0]])
        scene.add_object(dragon)

        statuette = SceneObject(statuette_mesh, color=(0.8, 0.6, 0.1))
        statuette.set_instances([[300.0, 0.0, -500.0]])
        scene.add_object(statuette)
    except Exception as exc:
        print(f"Error creating scene objects: {exc}")
        sys.exit(1)

    _add_default_lights(scene)


def setup_multiple_light_scenario(scene: Scene) -> None:
    """Configure the scene with a statuette and 50 point lights with varying colors.

    Loads the statuette model and adds 50 point lights with different colors distributed
    around the scene.

    Args:
        scene (Scene): The scene to configure.

    Returns:
        None
    """
    scene.clear()

    try:
        statuette_mesh = Mesh.load_from_file("assets/xyzrgb_statuette.obj")
    except Exception as exc:
        print(f"Error loading model: {exc}")
        sys.exit(1)

    statuette = SceneObject(statuette_mesh, color=(1.0, 1.0, 1.0))
    statuette.set_instances([[0.0, 0.0, -200.0]])
    scene.add_object(statuette)

    # Add 50 lights with different colors
    for i in range(50):
        x = np.random.uniform(-100, 100)
        y = np.random.uniform(-100, 100)
        z = np.random.uniform(-300, -100)
        r = np.random.uniform(0, 1)
        g = np.random.uniform(0, 1)
        b = np.random.uniform(0, 1)
        scene.add_light(PointLight(position=(x, y, z), color=(r, g, b)))


def setup_mega_grid_scenario(scene: Scene) -> None:
    """Configure a large 3D grid of instanced cubes for a stress test.

    Creates a dense grid of cube instances (~64000 instances) to benchmark instancing
    performance. Two default lights are attached after objects are created.

    Args:
        scene (Scene): The scene to configure.

    Returns:
        None
    """
    scene.clear()

    try:
        cube: Mesh = Mesh.load_from_file("assets/cube.obj")
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    obj = SceneObject(cube)
    # Generate ~40*40*40 instances in a 3D grid (spacing 1.5)
    offsets: List[List[float]] = [
        [x * 1.5, y * 1.5, z * 1.5]
        for x in range(-20, 20)
        for y in range(-20, 20)
        for z in range(-20, 20)
    ]
    obj.set_instances(offsets)
    scene.add_object(obj)

    _add_default_lights(scene)
