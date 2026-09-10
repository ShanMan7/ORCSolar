"""Boiler / solar-field evaporator.

This is where heat is added to the cycle - originally described in the
notebooks' comments as "temp out of boiler" and, per ORCModelReheat.ipynb's
driver-cell comment ("find temp levels for different DNI parabolic troughs"),
meant to represent heat collected from a concentrated-solar-thermal field
(e.g. a DNI-driven parabolic trough array). The model itself doesn't simulate
the solar field - it just takes the boiler-outlet (turbine-inlet) temperature
as an input and assumes the working fluid leaves as saturated vapor.
"""

from CoolProp.CoolProp import PropsSI

from ..state import State
from ..units import TK


def outlet_state(T1_celsius, fluid):
    """Saturated vapor leaving the boiler at turbine-inlet temperature T1 (deg C).

    Matches the state-1 calculation repeated in all three original notebooks:
    ``P1 = PropsSI('P','T|gas',TK(T1),'Q',1,F)`` etc.
    """
    T = TK(T1_celsius)
    P = PropsSI("P", "T|gas", T, "Q", 1, fluid)  # saturated vapor for a dry fluid
    s = PropsSI("S", "T|gas", T, "P", P, fluid)
    h = PropsSI("H", "T|gas", T, "P", P, fluid)
    return State(T=T, P=P, h=h, s=s)
