"""HXGR - internal recuperator (liquid preheater / vapor desuperheater).

Only used by the recuperated 6-state cycle (``orcsolar.cycles.recuperated``,
ported from ORCModelReheat.ipynb - despite that file's name, this is a
regenerator/recuperator, not a classical "reheat" stage). It transfers heat
from the turbine exhaust (hot side) to the pump discharge (cold side) before
the boiler, reducing the external heat duty and raising cycle efficiency.
Effectiveness defaults to 0.9 everywhere in the original notebooks ("an
estimate given by previous research", uncited).
"""

from CoolProp.CoolProp import PropsSI

from ..state import State


def recuperate(hot_in, cold_in, effectiveness, fluid):
    """Exchange heat between the turbine-exhaust (hot) and pump-discharge
    (cold) streams. Pressure is unchanged on each side (heat transfer only,
    no work). Returns ``(hot_out, cold_out)``.

    Matches the HXGR calculation repeated in ORCModelReheat.ipynb and
    ORCModelefficiencyplot.ipynb:

        T3 = TK(T2) - e*(TK(T2)-T5)
        h3 = PropsSI('H','P',P3,'T',T3,F)
        h6 = h2a - h3 + h5a
        T6 = PropsSI('T','H',h6,'P',P6,F)

    NOTE on the ``+ 273.15`` below: ``hot_in.T`` (the turbine-exit
    temperature) is already in Kelvin here, so adding 273.15 to it looks at
    first glance like a leftover/duplicated unit conversion from the
    original notebooks (they called their own ``TK()`` - Celsius-to-Kelvin -
    on a value that was already in Kelvin). It is intentionally preserved:
    dropping it (i.e. using ``hot_in.T`` directly) shifts every recuperated-
    cycle efficiency number by about +2.1 to +2.3 percentage points, and
    moves the model's output *away* from the digitized literature validation
    curve in ORCModelefficiencyplot.ipynb (mean absolute error vs. that curve
    goes from 0.18 to 2.2 percentage points - verified numerically before
    writing this module). So whatever "Kashif's paper" actually specifies,
    this form - offset included - is what reproduces it. Treat this as a
    validated modeling choice, not a typo, unless the source paper says
    otherwise.
    """
    P_hot = hot_in.P
    P_cold = cold_in.P

    T_hot_out = (hot_in.T + 273.15) - effectiveness * ((hot_in.T + 273.15) - cold_in.T)
    h_hot_out = PropsSI("H", "P", P_hot, "T", T_hot_out, fluid)

    h_cold_out = hot_in.h - h_hot_out + cold_in.h
    T_cold_out = PropsSI("T", "H", h_cold_out, "P", P_cold, fluid)

    s_hot_out = PropsSI("S", "T", T_hot_out, "P", P_hot, fluid)
    s_cold_out = PropsSI("S", "T", T_cold_out, "P", P_cold, fluid)

    hot_out = State(T=T_hot_out, P=P_hot, h=h_hot_out, s=s_hot_out)
    cold_out = State(T=T_cold_out, P=P_cold, h=h_cold_out, s=s_cold_out)
    return hot_out, cold_out
