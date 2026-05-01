import pytest
import numpy as np
from src.core.scene import Scene, Mesh
from src.core.scenarios import setup_village_scenario


def test_setup_village_scenario(mocker):
    mock_mesh = Mesh(np.array([]), np.array([]), np.array([]))
    mocker.patch('src.core.scene.Mesh.load_from_file', return_value=mock_mesh)

    scene = Scene()
    setup_village_scenario(scene)

    assert len(scene.objects) == 2
    assert len(scene.lights) == 2

    mocker.patch(
        "src.core.scene.Mesh.load_from_file", side_effect=Exception("File not found")
    )
    with pytest.raises(SystemExit):
        setup_village_scenario(scene)
