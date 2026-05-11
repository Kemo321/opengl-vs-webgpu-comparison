import pytest
import numpy as np
from src.core.scene import Scene, Mesh
from src.core.scenarios import setup_complex_object_scenario


def test_setup_complex_object_scenario(monkeypatch):
    mock_mesh = Mesh(np.array([]), np.array([]), np.array([]))
    monkeypatch.setattr(
        'src.core.scene.Mesh.load_from_file', lambda *a, **k: mock_mesh
    )

    scene = Scene()
    setup_complex_object_scenario(scene)

    assert len(scene.objects) == 3
    assert len(scene.lights) == 2

    def _raise(*a, **k):
        raise Exception("File not found")

    monkeypatch.setattr('src.core.scene.Mesh.load_from_file', _raise)
    with pytest.raises(SystemExit):
        setup_complex_object_scenario(scene)
