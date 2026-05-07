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


def setup_village_scenario(scene: Scene) -> None:
    """Configure the scene as a small village composed of simple instanced meshes.

    Loads models for walls and roofs, creates instance transforms for a few houses
    and attaches two default lights.

    Args:
        scene (Scene): The scene to configure.

    Returns:
        None
    """
    scene.clear()

    try:
        cube: Mesh = Mesh.load_from_file("assets/cube.obj")
        roof: Mesh = Mesh.load_from_file("assets/pyramid.obj")
    except Exception as exc:
        print(f"Error loading models: {exc}")
        sys.exit(1)

    house_offsets: List[List[float]] = [[-5, 0, -10], [0, 0, -15], [5, 0, -10]]

    walls = SceneObject(cube, color=(0.8, 0.5, 0.3))
    walls.set_instances(house_offsets)
    scene.add_object(walls)

    roof_offsets: List[List[float]] = [[p[0], p[1], p[2]] for p in house_offsets]
    roofs = SceneObject(roof, color=(0.7, 0.1, 0.1))
    roofs.set_instances(roof_offsets)
    scene.add_object(roofs)

    _add_default_lights(scene)


def setup_forest_scenario(scene: Scene) -> None:
    """Configure the scene as a dense forest using instanced trunks and canopies.

    Generates randomized ground-plane positions for a large number of tree instances
    and attaches two default lights.

    Args:
        scene (Scene): The scene to configure.

    Returns:
        None
    """
    scene.clear()

    try:
        trunk: Mesh = Mesh.load_from_file("assets/cylinder.obj")
        leaves: Mesh = Mesh.load_from_file("assets/cone.obj")
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    offsets: List[List[float]] = []
    for _ in range(1000):
        x = np.random.uniform(-30, 30)
        z = np.random.uniform(-50, -5)
        offsets.append([x, 0, z])

    trunks = SceneObject(trunk, color=(0.4, 0.2, 0.1))
    trunks.set_instances(offsets)
    scene.add_object(trunks)

    leaf_offsets_top: List[List[float]] = [[p[0], p[1] + 1.5, p[2]] for p in offsets]
    leaf_offsets_mid: List[List[float]] = [[p[0], p[1] + 0.5, p[2]] for p in offsets]
    leaf_offsets_low: List[List[float]] = [[p[0], p[1] + -0.5, p[2]] for p in offsets]
    forest_top = SceneObject(leaves, color=(0.1, 0.8, 0.1))
    forest_mid = SceneObject(leaves, color=(0.1, 0.8, 0.1))
    forest_low = SceneObject(leaves, color=(0.1, 0.8, 0.1))
    forest_top.set_instances(leaf_offsets_top)
    forest_mid.set_instances(leaf_offsets_mid)
    forest_low.set_instances(leaf_offsets_low)
    scene.add_object(forest_top)
    scene.add_object(forest_mid)
    scene.add_object(forest_low)

    _add_default_lights(scene)


def setup_mega_grid_scenario(scene: Scene) -> None:
    """Configure a large 3D grid of instanced cubes for a stress test.

    Creates a dense grid of cube instances (~27k instances) to benchmark instancing
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
    # Generate ~27,000 instances in a 3D grid (spacing 1.5)
    offsets: List[List[float]] = [
        [x * 1.5, y * 1.5, z * 1.5]
        for x in range(-15, 15)
        for y in range(-15, 15)
        for z in range(-30, 0)
    ]
    obj.set_instances(offsets)
    scene.add_object(obj)

    _add_default_lights(scene)
