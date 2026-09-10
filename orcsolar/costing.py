"""Purchased-equipment cost correlations (Turton/Guthrie-style log-quadratic
and power-law forms), attributed to "Kashif's paper" throughout the original
notebooks.

**Unvalidated - not wired into main.py.** Both source notebooks kept this
code disabled (commented out, never executed as part of a run), and
ORCModelReheat.ipynb's version is explicitly self-flagged by its own author
as "currently incorrect". These are ported here as real, importable functions
- instead of dead comments - purely so the work isn't lost while the package
is restructured. Don't trust any of these numbers without checking them
against the source paper first.
"""

import math

# --- from ORCModel (1).ipynb's commented-out cost cell (baseline cycle) ---


def condenser_cost_baseline(q_c):
    """q_c expected in kW, per the original comment."""
    return 12300 * (q_c / 50) ** 0.76


def pump_cost(wdot_p):
    return math.exp(3.3892 + 0.0536 * math.log(wdot_p) + 0.1538 * (math.log(wdot_p) ** 2))


def turbine_cost(wdot_t):
    return math.exp(2.2476 + 1.4965 * math.log(wdot_t) - 0.1618 * (math.log(wdot_t) ** 2))


def evaporator_cost_baseline(q_h):
    """q_h expected in W (the original divides by 1000 internally)."""
    return math.exp(3.2138 + 0.2688 * math.log(q_h / 1000) + 0.0796 * (math.log(q_h / 1000) ** 2))


# --- from ORCModelReheat.ipynb's commented-out cost cell (recuperated cycle) ---
# self-flagged in the original: "economic modelling, currently this is incorrect"


def condenser_cost_recuperated(q_c):
    return 12300 * (q_c / 50000) ** 0.76


def generator_cost(wdot_t):
    return 1850000 * (wdot_t / 11800000) ** 0.94


def hxgr_cost(delta_h_hot_side):
    """delta_h_hot_side = h2a - h3 in the original: the specific enthalpy
    drop across the recuperator's hot (turbine-exhaust) side."""
    return math.exp(
        4.3247 - 0.3030 * math.log(delta_h_hot_side) + 0.1634 * (math.log(delta_h_hot_side) ** 2)
    )


def evaporator_cost_recuperated(q_h):
    return math.exp(3.2138 + 0.2688 * math.log(q_h) + 0.0796 * (math.log(q_h) ** 2))
