"""
ui/app.py
---------
WaypointGeneratorApp — top-level application.
"""

import csv
import os
import tkinter as tk
from tkinter import messagebox

import numpy as np

from trajectories import TRAJECTORY_REGISTRY, LawnmowerTrajectory
from .controls import ControlsPanel
from .plot_panel import PlotPanel
from .theme import Theme as T

_WAYPOINT_ALGOS = {"Waypoints (sparse)"}


class WaypointGeneratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Waypoint Trajectory Generator")
        self.root.configure(bg=T.DARK_BG)
        self.root.geometry("1360x860")
        self.root.minsize(960, 620)

        self.waypoints: np.ndarray = np.empty((0, 2))
        self.headings: np.ndarray = np.empty((0,))

        self._build_layout()
        self._update()

    def _build_layout(self):
        self.controls = ControlsPanel(
            self.root,
            on_change=self._update,
            on_cable_change=self._reset_and_update,
            algo_names=list(TRAJECTORY_REGISTRY.keys()),
        )
        self.controls.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        self.controls.export_btn.config(command=self._export)

        self.plot = PlotPanel(self.root)
        self.plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _update(self, *_):
        try:
            p = self.controls.get_params()
            algo = self.controls.get_algo()
            klass = TRAJECTORY_REGISTRY.get(algo, LawnmowerTrajectory)
            traj = klass(**p)

            self.waypoints, self.headings = traj.generate_trajectory()

            is_wp_mode = algo in _WAYPOINT_ALGOS
            self.plot.draw(
                self.waypoints,
                self.headings,
                p,
                title=f"{algo} Trajectory",
                waypoint_mode=is_wp_mode,
            )

            n = len(self.waypoints)
            dur = (
                n / p["sampling_freq"] if (p["sampling_freq"] and not is_wp_mode) else 0
            )
            self.controls.set_info(
                f"Waypoints  : {n}\n"
                f"{'Duration   : ' + str(round(dur,1)) + ' s' if not is_wp_mode else 'Mode       : Sparse WP'}\n"
                f"Crossings  : {p['n_crossings']}\n"
                f"Angle (°)  : {p['angle_deg']:.1f}\n"
                f"Speed      : {p['drone_speed']:.1f} m/s\n"
                f"Sample Hz  : {p['sampling_freq']}\n"
                f"Heading    : nav (0°=N,CW)"
            )
        except Exception as exc:
            import traceback

            self.controls.set_info(f"Error:\n{exc}\n{traceback.format_exc()[-300:]}")

    def _reset_and_update(self, *_):
        self.plot.reset_view()
        self._update()

    def _export(self):
        if len(self.waypoints) == 0:
            messagebox.showwarning("Export", "No waypoints to export.")
            return
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(project_root, "save")
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, "waypoints.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["index", "latitude", "longitude", "heading"])
            for i, (lat, lon) in enumerate(self.waypoints):
                w.writerow(
                    [i + 1, f"{lat:.10f}", f"{lon:.10f}", f"{self.headings[i]:.4f}"]
                )
        messagebox.showinfo(
            "Export",
            f"Saved {len(self.waypoints)} waypoints to:\n{path}\n\n"
            f"Heading convention: 0°=North, 90°=East (clockwise)",
        )
