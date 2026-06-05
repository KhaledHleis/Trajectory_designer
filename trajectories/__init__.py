"""
trajectories/__init__.py
------------------------
Public API for the trajectories package.
"""

from .base import BaseTrajectory
from .lawnmower import LawnmowerTrajectory
from .parallel import ParallelTrajectory
from .zigzag import ZigzagTrajectory
from .waypoint import WaypointTrajectory

TRAJECTORY_REGISTRY: dict[str, type[BaseTrajectory]] = {
    "Lawnmower":       LawnmowerTrajectory,
    "Zigzag":          ZigzagTrajectory,
    "Parallel passes": ParallelTrajectory,
    "Waypoints (sparse)": WaypointTrajectory,
}

__all__ = [
    "BaseTrajectory",
    "LawnmowerTrajectory",
    "ParallelTrajectory",
    "ZigzagTrajectory",
    "WaypointTrajectory",
    "TRAJECTORY_REGISTRY",
]
