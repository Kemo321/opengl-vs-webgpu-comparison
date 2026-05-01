"""High-resolution frame profiler.

This module provides a lightweight profiler intended to be updated once
per rendered frame. It tracks frame counts and periodically computes
frames per second (FPS) together with the corresponding average frame
time in milliseconds.
"""

import time


class Profiler:
    """Track frame timing and derive FPS metrics.

    Attributes:
        last_time (float): Timestamp of the last metrics update.
        frames (int): Number of frames counted since the last update.
        fps (float): Most recently computed frames per second value.
        frame_time_ms (float): Most recently computed frame time in milliseconds.
    """

    def __init__(self) -> None:
        self.last_time: float = time.perf_counter()
        self.frames: int = 0
        self.fps: float = 0.0
        self.frame_time_ms: float = 0.0

    def update(self) -> bool:
        """Record one frame and refresh metrics when needed.

        Call this once per rendered frame. Metrics are recomputed at
        approximately one-second intervals.

        Returns:
            bool: True when FPS and frame time were refreshed; otherwise False.
        """
        current_time = time.perf_counter()

        self.frames += 1

        delta_time = current_time - self.last_time

        if delta_time >= 1.0:
            self.fps = self.frames / delta_time

            self.frame_time_ms = (1000.0 / self.fps) if self.fps > 0.0 else 0.0

            self.frames = 0
            self.last_time = current_time
            return True

        return False
