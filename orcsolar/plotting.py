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


def plot_chiller_ts(result, mixture, filename="chiller_ts_diagram.png", output_dir="figures"):
    """T-s diagram of the chiller's REFRIGERANT loop (states 1-4).

    The solution loop (a-d) is deliberately absent. It is a LiBr-water mixture
    at two different concentrations, so it does not belong on the pure-water
    saturation dome, and its entropy is not available on a datum that is
    consistent across concentrations. Use ``plot_chiller_duehring`` to see it.

    The 1 -> 2 leg is drawn dashed because that is not a process on this plane:
    it is the thermal compressor - absorber, pump, generator - which raises the
    refrigerant from low to high pressure by dissolving and re-boiling it.
    """
    from CoolProp.CoolProp import PropsSI

    from .ts_diagram import saturation_dome
    from .units import TC, TK

    refrigerant = mixture.REFRIGERANT
    s = result["states"]
    T_evap = result["inputs"]["T_evaporator"]
    T_cond = result["inputs"]["T_condenser"]

    fig, ax = plt.subplots(figsize=(8, 6))

    T_dome, s_dome = saturation_dome(refrigerant, n_points=400)
    ax.plot(s_dome, [TC(t) for t in T_dome], color="0.6", lw=1, label=f"{refrigerant} saturation dome")

    pt = {k: (s[k].s, TC(s[k].T)) for k in "1234"}

    # Saturated vapor at condenser pressure - the corner between desuperheating
    # and condensing.
    s_g_cond = PropsSI("S", "T", TK(T_cond), "Q", 1, refrigerant)

    # 2 -> 3  desuperheat then condense (constant pressure)
    ax.plot([pt["2"][0], s_g_cond, pt["3"][0]], [pt["2"][1], T_cond, T_cond],
            color="tab:red", lw=2, label="2->3 condenser")
    # 3 -> 4  throttle (isenthalpic, irreversible - entropy rises)
    ax.plot([pt["3"][0], pt["4"][0]], [pt["3"][1], pt["4"][1]],
            color="tab:orange", lw=2, label="3->4 throttle")
    # 4 -> 1  evaporate (constant temperature)
    ax.plot([pt["4"][0], pt["1"][0]], [T_evap, T_evap],
            color="tab:blue", lw=2, label="4->1 evaporator (cooling)")
    # 1 -> 2  not a path on this plane
    ax.plot([pt["1"][0], pt["2"][0]], [pt["1"][1], pt["2"][1]],
            color="tab:green", lw=1.5, ls="--", label="1->2 thermal compressor")

    for k, (sv, tv) in pt.items():
        ax.plot(sv, tv, "o", color="k", ms=6, zorder=5)
        ax.annotate(k, (sv, tv), textcoords="offset points", xytext=(7, 5),
                    fontsize=11, fontweight="bold")

    ax.set_xlabel("s (J/kg-K)")
    ax.set_ylabel("T (C)")
    ax.set_title(
        f"Absorption chiller, refrigerant loop - {refrigerant}\n"
        f"COP {result['cop']:.3f},  f {result['f']:.2f},  "
        f"cooling {result['q_evap']/1000:.0f} kJ/kg"
    )
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)
    return _save(fig, output_dir, filename)


def plot_chiller_duehring(result, mixture, filename="chiller_duehring.png", output_dir="figures"):
    """Duehring plot (pressure vs solution temperature, lines of constant
    concentration) - the standard absorption-cycle diagram, and the one that
    actually shows the solution loop.

    The cycle appears as a quadrilateral a -> b -> c -> d. Its horizontal
    extent is the degassing width: the wider the box, the more refrigerant each
    kg of circulated solution carries, and the lower the circulation ratio.
    """
    import numpy as np

    from .units import TC

    s = result["states"]
    fig, ax = plt.subplots(figsize=(8, 6))

    # Constant-concentration lines spanning the operating range
    x_lo = max(0.40, result["x_strong"] - 0.10)
    x_hi = min(mixture.X_MAX, result["x_weak"] + 0.06)
    for x in np.linspace(x_lo, x_hi, 7):
        T_line = np.linspace(20, 140, 60)
        P_line = [mixture.P_saturated(t, x) for t in T_line]
        ax.plot(T_line, P_line, color="0.75", lw=0.8)
        ax.annotate(f"{x*100:.0f}%", (T_line[-1], P_line[-1]), fontsize=7,
                    color="0.45", textcoords="offset points", xytext=(2, 0))

    order = ["a", "b", "c", "d", "a"]
    T_cycle = [TC(s[k].T) for k in order]
    P_cycle = [s[k].P for k in order]
    ax.plot(T_cycle, P_cycle, "-o", color="tab:purple", lw=2, ms=6, zorder=5)

    for k in "abcd":
        ax.annotate(f"{k}  (x={s[k].x:.3f})", (TC(s[k].T), s[k].P),
                    textcoords="offset points", xytext=(8, -4), fontsize=9)

    ax.set_yscale("log")
    ax.set_xlabel("solution temperature (C)")
    ax.set_ylabel("pressure (Pa, log scale)")
    ax.set_title(
        f"Absorption chiller, solution loop - Duehring plot\n"
        f"degassing width {result['degassing_width']:.4f} "
        f"({result['x_strong']:.3f} -> {result['x_weak']:.3f} LiBr)"
    )
    ax.grid(alpha=0.3, which="both")
    return _save(fig, output_dir, filename)
