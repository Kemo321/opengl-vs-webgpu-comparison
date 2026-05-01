import pytest
from src.core.profiler import Profiler


def test_profiler_initial_state():
    p = Profiler()
    assert p.frames == 0
    assert p.fps == 0.0
    assert p.frame_time_ms == 0.0


def test_profiler_update_no_refresh(mocker):
    mocker.patch("time.perf_counter", side_effect=[0.0, 0.5])
    p = Profiler()
    p.last_time = 0.0

    updated = p.update()
    assert updated is False
    assert p.frames == 1


def test_profiler_update_with_refresh(mocker):
    mocker.patch("time.perf_counter", side_effect=[0.0, 1.0])
    p = Profiler()
    p.last_time = 0.0
    p.frames = 59

    updated = p.update()
    assert updated is True
    assert p.fps == 60.0
    assert p.frame_time_ms == pytest.approx(1000.0 / 60.0)
    assert p.frames == 0
