"""Baseline subcritical ORC: boiler -> turbine -> condenser -> pump -> (back
to boiler). Four thermodynamic states, no internal heat recovery.

Ported from ORCModel (1).ipynb's ``runCycle`` / ``efficiencyPlot``. Verified
against the original notebook's own cached output: at T1=185 C, T3=35 C,
``run_cycle`` reproduces MM 16.3%, ISOPENTANE 18.3%, HEPTANE 18.9%,
TOLUENE 21.8%, NOCTANE 18.9%, CYCLOPENTANE 21.1% exactly.
"""

import math

from CoolProp.CoolProp import PropsSI

from ..components import boiler, condenser, pump, turbine
from ..ts_diagram import saturation_dome
from ..units import TC, TK

DEFAULT_ETA_TURBINE = 0.85  # isentropic turbine efficiency ("Kashif's paper")
DEFAULT_ETA_PUMP = 0.65  # isentropic pump efficiency ("Kashif's paper")

# ORCModel (1).ipynb's efficiencyPlot() hardcoded the condenser temperature to
# 50 C internally (not a parameter), while its driver cell called runCycle()
# separately with T3=35 C for the T-s diagrams. That's a real inconsistency
# in the original notebook, not a typo we can resolve on its behalf - both
# defaults are preserved below, matching each function's original behavior.
DEFAULT_T_COND_SWEEP = 50


def solve_states(T1, T3, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP):
    """Solve all four state points for one pass of the cycle. No plotting,
    no printing - the cheap, reusable core used by both ``run_cycle`` (single
    detailed point) and ``efficiency_sweep`` (many points, fast)."""
    s1 = boiler.outlet_state(T1, fluid)
    s3 = condenser.outlet_state(T3, fluid)

    s2, wdot_t = turbine.expand(s1, P_out=s3.P, eta_isentropic=eta_turbine, fluid=fluid)
    s4, wdot_p = pump.compress(s3, P_out=s1.P, eta_isentropic=eta_pump, fluid=fluid)

    q_h = s1.h - s4.h
    q_c = s2.h - s3.h
    eta = 100 * (-wdot_t + wdot_p) / -q_h

    return {
        "states": {"1": s1, "2": s2, "3": s3, "4": s4},
        "wdot_t": wdot_t,
        "wdot_p": wdot_p,
        "q_h": q_h,
        "q_c": q_c,
        "eta": eta,
    }


def run_cycle(T1, T3, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP,
              verbose=False, include_dome=True):
    """Solve one cycle and (by default) attach the saturation dome, matching
    the original ``runCycle``'s return value (state points + T-s dome data)."""
    result = solve_states(T1, T3, fluid, eta_turbine, eta_pump)

    if verbose:
        print("the efficiency is", result["eta"], "percent")
        print("pump work: ", result["wdot_p"] / 1000, " kJ/kg")
        print("turbine work: ", result["wdot_t"] / 1000, " kJ/kg")

    if include_dome:
        result["dome_T"], result["dome_s"] = saturation_dome(fluid)

    return result


def efficiency_sweep(fluid, T_cond=DEFAULT_T_COND_SWEEP, eta_turbine=DEFAULT_ETA_TURBINE,
                      eta_pump=DEFAULT_ETA_PUMP, T1_start=100):
    """Sweep turbine-inlet temperature from ``T1_start`` (deg C) up to the
    fluid's critical temperature. Returns ``(inlet_temperatures_K,
    efficiencies_pct)`` - inlet temperatures in Kelvin, matching the original
    ``efficiencyPlot``.

    Uses ``solve_states`` directly (not ``run_cycle``) so the saturation dome
    isn't recomputed on every one of the ~100+ sweep points.
    """
    highT = math.floor(TC(PropsSI("Tcrit", fluid)))
    inlet_temperatures = []
    efficiencies = []
    for T1 in range(T1_start, highT):
        result = solve_states(T1, T_cond, fluid, eta_turbine, eta_pump)
        inlet_temperatures.append(TK(T1))
        efficiencies.append(result["eta"])
    return inlet_temperatures, efficiencies
