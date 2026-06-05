"""
trajectories/base.py
--------------------
Abstract base class shared by all trajectory algorithms.

Coordinate system
-----------------
Cable endpoints are given in (lat, lon) decimal degrees.
Drone speed is given in **m/s** and converted internally to deg/s using
a local flat-Earth approximation at the cable's mean latitude.

Heading convention
------------------
All headings are in **navigation convention**:
  0° = North, 90° = East, 180° = South, 270° = West  (clockwise from North)
Range: [0, 360)
"""

import math
from abc import ABC, abstractmethod

import numpy as np

_METRES_PER_DEG_LAT = 111_320.0


def direction_to_heading(dlat: float, dlon: float) -> float:
    """
    Convert a (dlat, dlon) direction vector to navigation heading [0, 360).
    North = 0°, East = 90°.
    """
    h = math.degrees(math.atan2(dlon, dlat))  # atan2(east, north)
    return h % 360.0


class BaseTrajectory(ABC):
    """
    Parameters
    ----------
    cable_p1, cable_p2 : (lat, lon) tuples defining the cable endpoints
    sampling_freq      : sample rate [Hz]
    drone_speed        : linear speed [m/s]
    """

    def __init__(self, cable_p1, cable_p2, sampling_freq, drone_speed):
        self.cable_p1 = np.array(cable_p1, dtype=float)
        self.cable_p2 = np.array(cable_p2, dtype=float)
        self.sampling_freq = float(sampling_freq)
        self.drone_speed = float(drone_speed)

        lat_mean = math.radians((cable_p1[0] + cable_p2[0]) / 2.0)
        self._m_per_deg_lat = _METRES_PER_DEG_LAT
        self._m_per_deg_lon = _METRES_PER_DEG_LAT * math.cos(lat_mean)
        # isotropic approximation
        self._m_per_deg = (self._m_per_deg_lat + self._m_per_deg_lon) / 2.0
        self._speed_deg_s = self.drone_speed / self._m_per_deg

    # ── unit helpers ──────────────────────────────────────────────────────────

    def metres_to_deg(self, metres: float) -> float:
        return metres / self._m_per_deg

    def deg_to_metres(self, degrees: float) -> float:
        return degrees * self._m_per_deg

    @abstractmethod
    def generate_trajectory(self) -> tuple[np.ndarray, np.ndarray]:
        """Return ((N,2) array of (lat,lon), (N,) array of headings in deg)."""

    # ── sampling helpers ──────────────────────────────────────────────────────

    def _sample_segment(self, p_start: np.ndarray, p_end: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Uniformly sample a straight segment. Returns (pts, headings)."""
        d = p_end - p_start
        dist_deg = np.linalg.norm(d)
        if dist_deg < 1e-12:
            h = direction_to_heading(0.0, 0.0)
            return p_start.reshape(1, 2), np.array([h])
        dist_m = self.deg_to_metres(dist_deg)
        n = max(2, int(dist_m / self.drone_speed * self.sampling_freq))
        t = np.linspace(0, 1, n)
        pts = p_start + np.outer(t, d)
        heading = direction_to_heading(d[0], d[1])
        headings = np.full(n, heading)
        return pts, headings

    def _sample_arc(
        self, centre: np.ndarray, radius_deg: float, a_start: float, a_end: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Sample a circular arc. a_start/a_end are math angles (CCW from +lat axis).
        Returns (pts, headings) where headings follow navigation convention.
        """
        arc_len_deg = abs(a_end - a_start) * radius_deg
        if arc_len_deg < 1e-12:
            pt = centre + radius_deg * np.array([math.cos(a_start), math.sin(a_start)])
            heading = direction_to_heading(
                -math.sin(a_start) * (1 if a_end >= a_start else -1),
                math.cos(a_start) * (1 if a_end >= a_start else -1),
            )
            return pt.reshape(1, 2), np.array([heading])
        arc_len_m = self.deg_to_metres(arc_len_deg)
        n = max(4, int(arc_len_m / self.drone_speed * self.sampling_freq))
        angles = np.linspace(a_start, a_end, n)
        pts = centre + radius_deg * np.column_stack([np.cos(angles), np.sin(angles)])
        # tangent direction: CCW orbit => tangent = (-sin a, cos a), CW => (sin a, -cos a)
        ccw = (a_end > a_start)
        sign = 1.0 if ccw else -1.0
        dlat = -np.sin(angles) * sign
        dlon = np.cos(angles) * sign
        headings = np.array([direction_to_heading(la, lo) for la, lo in zip(dlat, dlon)])
        return pts, headings
