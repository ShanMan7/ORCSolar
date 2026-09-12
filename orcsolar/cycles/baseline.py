"""Baseline subcritical ORC, assembled from the parts in orcsolar.components:

    boiler -> turbine -> condenser -> pump -> back to boiler

Four state points:

    1   boiler outlet / turbine inlet     saturated vapor at T1
    2   turbine outlet                    expanded to condenser pressure
    3   condenser outlet / pump inlet     saturated liquid at T3
    4   pump outlet / boiler inlet        compressed to boiler pressure
"""

import CoolProp.CoolProp as CP

from ..components import boiler, condenser, pump, turbine

DEFAULT_ETA_TURBINE = 0.85  # isentropic turbine efficiency ("Kashif's paper")
DEFAULT_ETA_PUMP = 0.65  # isentropic pump efficiency ("Kashif's paper")


def solve_states(T1, T3, fluid, eta_turbine=DEFAULT_ETA_TURBINE, eta_pump=DEFAULT_ETA_PUMP):
    """Walk the cycle once, calling each component in turn.

    T1: turbine-inlet (boiler-outlet) temperature, deg C
    T3: condenser-outlet (pump-inlet) temperature, deg C

    Returns a dict holding the four states, the per-unit-mass work and heat
    terms (J/kg), and the thermal efficiency (%).
    """
    # Enthalpy and entropy only mean anything relative to a datum. Pin it to
    # the normal boiling point so this cycle's state table and the
    # recuperated one's are directly comparable. Efficiency is unaffected
    # either way - it's built from differences, so the datum cancels.
    CP.set_reference_state(fluid, "NBP")

    # The two saturated states set the cycle's two pressure levels...
    s1 = boiler.outlet_state(T1, fluid)
    s3 = condenser.outlet_state(T3, fluid)

    # ...and the two work devices move the fluid between them.
    s2, w_turbine = turbine.expand(s1, s3.P, eta_turbine, fluid)
    s4, w_pump = pump.compress(s3, s1.P, eta_pump, fluid)

    q_in = s1.h - s4.h  # boiler, state 4 -> 1
    q_out = s2.h - s3.h  # condenser, state 2 -> 3
    w_net = w_turbine - w_pump
    eta = 100 * w_net / q_in

    return {
        "fluid": fluid,
        "states": {"1": s1, "2": s2, "3": s3, "4": s4},
        "w_turbine": w_turbine,
        "w_pump": w_pump,
        "w_net": w_net,
        "q_in": q_in,
        "q_out": q_out,
        "eta": eta,
    }
