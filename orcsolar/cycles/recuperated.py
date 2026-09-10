"""Regenerative ("recuperated") ORC: boiler -> turbine -> HXGR (hot side) ->
condenser -> pump -> HXGR (cold side) -> back to boiler. Six thermodynamic
states.

Ported from ORCModelReheat.ipynb's ``runCycle`` / ``efficiencyPlot``. Despite
that notebook's filename, this is a recuperator/regenerator, not a classical
reheat stage - a single turbine, plus an internal heat exchanger ("HXGR")
that preheats the pump discharge using turbine-exhaust heat. Verified against
the original notebook's own cached output: at T1=185 C, T4=35 C, HEPTANE,
``run_cycle`` reproduces 21.0% / 22.1% / 23.1% efficiency for turbine
isentropic efficiencies of 0.80 / 0.85 / 0.90 exactly.
"""

import math

import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI

from ..components import boiler, condenser, hxgr, pump, turbine
from ..ts_diagram import saturation_dome
from ..units import TC

DEFAULT_ETA_TURBINE = 0.85  # isentropic turbine efficiency ("Kashif's paper")
DEFAULT_ETA_PUMP = 0.65  # isentropic pump efficiency ("Kashif's paper")
DEFAULT_EFFECTIVENESS = 0.9  # HXGR effectiveness ("an estimate given by previous research")
DEFAULT_T_COND = 35


def solve_states(T1, T4, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP,
                  effectiveness=DEFAULT_EFFECTIVENESS):
    """Solve all six state points for one pass of the cycle. No plotting, no
    printing - the cheap, reusable core used by both ``run_cycle`` (single
    detailed point) and ``efficiency_sweep`` (many points, fast)."""
    s1 = boiler.outlet_state(T1, fluid)
    s4 = condenser.outlet_state(T4, fluid)

    s2, wdot_t = turbine.expand(s1, P_out=s4.P, eta_isentropic=eta_turbine, fluid=fluid)
    s5, wdot_p = pump.compress(s4, P_out=s1.P, eta_isentropic=eta_pump, fluid=fluid)

    s3, s6 = hxgr.recuperate(hot_in=s2, cold_in=s5, effectiveness=effectiveness, fluid=fluid)

    q_h = s1.h - s6.h
    q_c = s3.h - s4.h
    eta = 100 * (-wdot_t + wdot_p) / -q_h

    return {
        "states": {"1": s1, "2": s2, "3": s3, "4": s4, "5": s5, "6": s6},
        "wdot_t": wdot_t,
        "wdot_p": wdot_p,
        "q_h": q_h,
        "q_c": q_c,
        "eta": eta,
    }


def run_cycle(T1, T4, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP,
              effectiveness=DEFAULT_EFFECTIVENESS, verbose=False, include_dome=True):
    """Solve one cycle and (by default) attach the saturation dome, matching
    the original ``runCycle``'s return value (state points + T-s dome data).

    Also matches the original's ``CP.set_reference_state(F, 'NBP')`` call -
    this only shifts the reference (zero) point for enthalpy/entropy, which
    cancels out of every efficiency/work calculation here since those are
    all computed from differences; it's preserved purely for byte-for-byte
    fidelity with the original notebook's printed diagnostics.
    """
    CP.set_reference_state(fluid, "NBP")
    result = solve_states(T1, T4, fluid, eta_turbine, eta_pump, effectiveness)
    states = result["states"]

    if verbose:
        s12 = states["2"].s - states["1"].s
        s23 = states["3"].s - states["2"].s
        s34 = states["4"].s - states["3"].s
        s45 = states["5"].s - states["4"].s
        s56 = states["6"].s - states["5"].s
        s61 = states["1"].s - states["6"].s

        print("the efficiency for " + fluid + " is", result["eta"], "percent")
        print("pump work: ", result["wdot_p"] / 1000, " kJ/kg")
        print("turbine work: ", result["wdot_t"] / 1000, " kJ/kg")
        print(
            "Temperatures (1 to 6 in order): ",
            T1, TC(states["2"].T), TC(states["3"].T), T4, TC(states["5"].T), TC(states["6"].T),
        )
        print(
            "Pressures (1 to 6 in order): ",
            states["1"].P, states["2"].P, states["3"].P, states["4"].P, states["5"].P, states["6"].P,
        )
        print(
            "Entropies (1 to 6 in order): ",
            states["1"].s, states["2"].s, states["3"].s, states["4"].s, states["5"].s, states["6"].s,
        )
        print("Change in Entropies: ", s12, s23, s34, s45, s56, s61)

    if include_dome:
        result["dome_T"], result["dome_s"] = saturation_dome(fluid)

    return result


def efficiency_sweep(fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP,
                      effectiveness=DEFAULT_EFFECTIVENESS, T_cond=DEFAULT_T_COND, T1_start=100):
    """Sweep turbine-inlet temperature from ``T1_start`` (deg C) up to the
    fluid's critical temperature. Returns ``(inlet_temperatures_C,
    efficiencies_pct)`` - inlet temperatures in Celsius, matching the
    original ``efficiencyPlot``.

    Uses ``solve_states`` directly (not ``run_cycle``) so the saturation dome
    isn't recomputed on every one of the ~100+ sweep points.
    """
    highT = math.floor(TC(PropsSI("Tcrit", fluid)))
    inlet_temperatures = []
    efficiencies = []
    for T1 in range(T1_start, highT):
        result = solve_states(T1, T_cond, fluid, eta_turbine, eta_pump, effectiveness)
        inlet_temperatures.append(T1)
        efficiencies.append(result["eta"])
    return inlet_temperatures, efficiencies
