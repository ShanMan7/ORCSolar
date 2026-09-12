"""Recuperated ORC, assembled from the parts in orcsolar.components:

    boiler -> turbine -> HXGR (hot side) -> condenser -> pump -> HXGR (cold side)

Same four components as the baseline cycle, plus an internal recuperator
that moves heat from the turbine exhaust into the pump discharge before the
boiler - so the boiler has less work to do for the same turbine inlet state.

Six state points:

    1   boiler outlet / turbine inlet     saturated vapor at T1
    2   turbine outlet / HXGR hot in      expanded to condenser pressure
    3   HXGR hot out / condenser inlet    desuperheated turbine exhaust
    4   condenser outlet / pump inlet     saturated liquid at T4
    5   pump outlet / HXGR cold in        compressed to boiler pressure
    6   HXGR cold out / boiler inlet      preheated feed
"""

import CoolProp.CoolProp as CP

from ..components import boiler, condenser, hxgr, pump, turbine

DEFAULT_ETA_TURBINE = 0.85  # isentropic turbine efficiency ("Kashif's paper")
DEFAULT_ETA_PUMP = 0.65  # isentropic pump efficiency ("Kashif's paper")
DEFAULT_EFFECTIVENESS = 0.9  # HXGR effectiveness ("an estimate given by previous research")


def solve_states(T1, T4, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP,
                  effectiveness=DEFAULT_EFFECTIVENESS):
    """Walk the cycle once, calling each component in turn.

    T1: turbine-inlet (boiler-outlet) temperature, deg C
    T4: condenser-outlet (pump-inlet) temperature, deg C

    Returns a dict holding the six states, the per-unit-mass work and heat
    terms (J/kg), and the thermal efficiency (%).
    """
    # See the note in cycles/baseline.py - pinned so both cycles' state
    # tables share one datum. Efficiency is unaffected.
    CP.set_reference_state(fluid, "NBP")

    # The two saturated states set the cycle's two pressure levels...
    s1 = boiler.outlet_state(T1, fluid)
    s4 = condenser.outlet_state(T4, fluid)

    # ...the two work devices move the fluid between them...
    s2, w_turbine = turbine.expand(s1, s4.P, eta_turbine, fluid)
    s5, w_pump = pump.compress(s4, s1.P, eta_pump, fluid)

    # ...and the recuperator links the two sides, cooling the turbine
    # exhaust (2 -> 3) to preheat the pump discharge (5 -> 6).
    s3, s6 = hxgr.recuperate(s2, s5, effectiveness, fluid)

    q_in = s1.h - s6.h  # boiler, state 6 -> 1
    q_out = s3.h - s4.h  # condenser, state 3 -> 4
    q_recuperated = s2.h - s3.h  # heat kept inside the cycle
    w_net = w_turbine - w_pump
    eta = 100 * w_net / q_in

    return {
        "fluid": fluid,
        "states": {"1": s1, "2": s2, "3": s3, "4": s4, "5": s5, "6": s6},
        "w_turbine": w_turbine,
        "w_pump": w_pump,
        "w_net": w_net,
        "q_in": q_in,
        "q_out": q_out,
        "q_recuperated": q_recuperated,
        "eta": eta,
    }
