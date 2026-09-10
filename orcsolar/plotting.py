"""Plot builders mirroring the figures the three original notebooks produced
inline. Every function here saves a PNG under ``output_dir`` (default
``figures/``, created if needed) and returns its path, so results persist as
real files instead of only living inside a notebook cell output.
"""

import os

import matplotlib.pyplot as plt


def _save(fig, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_efficiency_curves(curves, xlabel, title, filename, output_dir="figures"):
    """curves: ``{label: (x_values, y_values)}``. One line per label."""
    fig, ax = plt.subplots()
    for label, (xs, ys) in curves.items():
        ax.plot(xs, ys, label=str(label))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Efficiency (%)")
    ax.set_title(title)
    ax.legend()
    return _save(fig, output_dir, filename)


def plot_ts_diagram(dome_curves, overlay_points=None, title="T-s diagram",
                     filename="ts_diagram.png", output_dir="figures", temp_label="T (K)"):
    """dome_curves: ``{label: (s_values, T_values)}`` saturation dome(s),
    drawn as lines. overlay_points: optional ``{label: (s_values, T_values)}``
    of discrete cycle state points, drawn as markers on top."""
    fig, ax = plt.subplots()
    for label, (s_vals, T_vals) in dome_curves.items():
        ax.plot(s_vals, T_vals, label=str(label))
    if overlay_points:
        for label, (s_vals, T_vals) in overlay_points.items():
            ax.plot(s_vals, T_vals, "o", label=str(label))
    ax.set_xlabel("s (J/kg-K)")
    ax.set_ylabel(temp_label)
    ax.set_title(title)
    ax.legend()
    return _save(fig, output_dir, filename)


def plot_calibration_overlay(model_xy, calibration_xy, fluid,
                              filename="calibration_overlay.png", output_dir="figures"):
    """model_xy / calibration_xy: ``(x_values, y_values)`` pairs to compare -
    model curve as a line, digitized literature points as markers."""
    fig, ax = plt.subplots()
    ax.plot(*calibration_xy, "o", label="Literature (digitized)")
    ax.plot(*model_xy, label="Model")
    ax.set_xlabel("Inlet Temperature (C)")
    ax.set_ylabel("Efficiency (%)")
    ax.set_title(f"Inlet Temp vs Efficiency for {fluid}")
    ax.legend()
    return _save(fig, output_dir, filename)
