"""Turbine.

Expands the working fluid from boiler pressure down to condenser pressure,
producing shaft work, at a fixed isentropic efficiency (all three notebooks
default this to 0.85, attributed to "Kashif's paper").
"""

from CoolProp.CoolProp import PropsSI

from ..state import State


def expand(state_in, P_out, eta_isentropic, fluid):
    """Expand ``state_in`` down to ``P_out`` at the given isentropic efficiency.

    Matches the turbine calculation repeated in all three original notebooks:
    ``h2s = PropsSI('H','P',P2,'S',s1,F); h2a = h1 - nt*(h1-h2s)`` etc.

    Returns ``(state_out, specific_work)`` where ``specific_work`` is the
    work produced per unit mass (J/kg), matching the original sign
    convention (``wdot_t = h1 - h2a``, positive when the turbine does work
    on its surroundings).
    """
    h_out_isentropic = PropsSI("H", "P", P_out, "S", state_in.s, fluid)
    h_out = state_in.h - eta_isentropic * (state_in.h - h_out_isentropic)
    s_out = PropsSI("S", "H", h_out, "P", P_out, fluid)
    T_out = PropsSI("T", "P", P_out, "S", s_out, fluid)

    work = state_in.h - h_out
    return State(T=T_out, P=P_out, h=h_out, s=s_out), work
