import numpy as np
from src.core.scene import Scene, SceneObject, PointLight, Mesh


def test_scene_management():
    scene = Scene()
    mesh = Mesh(np.array([]), np.array([]), np.array([]))
    obj = SceneObject(mesh, color=(1, 0, 0))
    light = PointLight(position=(0, 10, 0), color=(1, 1, 1))

    scene.add_object(obj)
    scene.add_light(light)

    assert len(scene.objects) == 1
    assert len(scene.lights) == 1

    scene.clear()
    assert len(scene.objects) == 0
    assert len(scene.lights) == 0


def test_scene_object_instancing():
    mesh = Mesh(np.array([]), np.array([]), np.array([]))
    obj = SceneObject(mesh)

    offsets = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]
    obj.set_instances(offsets)

    assert len(obj.instance_offsets) == 2
    assert obj.instance_offsets[0].x == 1.0
