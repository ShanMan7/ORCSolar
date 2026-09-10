"""Condenser.

Rejects heat to the cold sink (ambient / cooling water), leaving the working
fluid as saturated liquid at the condenser temperature.
"""

from CoolProp.CoolProp import PropsSI

from ..state import State
from ..units import TK


def outlet_state(T_cond_celsius, fluid):
    """Saturated liquid leaving the condenser at T_cond (deg C).

    Matches the "through condenser" state calculation repeated in all three
    original notebooks: ``P3/P4 = PropsSI('P','T|liquid',TK(T3/T4),'Q',0,F)`` etc.
    (called state 3 in the baseline 4-state cycle, state 4 in the recuperated
    6-state cycle - see ``orcsolar.cycles``).
    """
    T = TK(T_cond_celsius)
    P = PropsSI("P", "T|liquid", T, "Q", 0, fluid)  # saturated liquid
    s = PropsSI("S", "T|liquid", T, "P", P, fluid)
    h = PropsSI("H", "T|liquid", T, "P", P, fluid)
    return State(T=T, P=P, h=h, s=s)
