"""Feed pump.

Compresses saturated liquid from condenser pressure back up to boiler
pressure, consuming shaft work, at a fixed isentropic efficiency (all three
notebooks default this to 0.65, attributed to "Kashif's paper").
"""

from CoolProp.CoolProp import PropsSI

from ..state import State


def compress(state_in, P_out, eta_isentropic, fluid):
    """Compress ``state_in`` up to ``P_out`` at the given isentropic efficiency.

    Matches the pump calculation repeated in all three original notebooks:
    ``h4s = PropsSI('H','P',P4,'S',s3,F); h4a = h3 - np*(h3-h4s)`` etc.

    Returns ``(state_out, specific_work)`` where ``specific_work`` is the
    work consumed per unit mass (J/kg), matching the original sign
    convention (``wdot_p = h4a - h3``, positive since enthalpy rises across
    the pump).
    """
    h_out_isentropic = PropsSI("H", "P", P_out, "S", state_in.s, fluid)
    h_out = state_in.h - eta_isentropic * (state_in.h - h_out_isentropic)
    T_out = PropsSI("T", "P", P_out, "H", h_out, fluid)
    s_out = PropsSI("S", "T|liquid", T_out, "P", P_out, fluid)

    work = h_out - state_in.h
    return State(T=T_out, P=P_out, h=h_out, s=s_out), work
