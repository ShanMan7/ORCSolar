"""General two-stream heat exchanger (the blue squares in the system diagram).

Distinct from ``hxgr.py``, which is the ORC's internal recuperator: that one
carries the *same* fluid at the *same* mass flow on both sides and is written
in per-unit-mass terms. This one connects two different loops - solar water to
storage, storage to the ORC boiler, chiller to chilled-water - so the two sides
generally carry different fluids at different flow rates, and it works in
Streams.

Only the *definition* of effectiveness is implemented here:

    C_side = mdot * cp                  (capacity rate, W/K)
    Q_max  = C_min * (T_hot_in - T_cold_in)
    Q      = effectiveness * Q_max

Effectiveness itself is an input. Deriving it from geometry (the epsilon-NTU
correlations, which differ for counterflow, parallel flow, shell-and-tube,
etc.) is a separate modeling choice and is deliberately not assumed here.
"""

from CoolProp.CoolProp import PropsSI

from ..state import Stream, state_from_Ph


def transfer(hot_in, cold_in, effectiveness):
    """Exchange heat between two streams at the given effectiveness.

    Returns ``(hot_out, cold_out, Q)`` with Q in W, positive from hot to cold.
    Pressure is unchanged on both sides (no pressure-drop model).

    Note: capacity rates use cp evaluated at each stream's *inlet* condition.
    That linearization is standard for design-point work but degrades if either
    stream changes phase or spans a large temperature range - if you add a
    two-phase side later, this is the assumption to revisit.
    """
    if effectiveness < 0.0 or effectiveness > 1.0:
        raise ValueError(f"effectiveness must be in [0, 1], got {effectiveness}")

    if hot_in.T <= cold_in.T:
        raise ValueError(
            f"hot stream ({hot_in.T:.2f} K) is not hotter than the cold stream "
            f"({cold_in.T:.2f} K) - heat will not flow in the assumed direction"
        )

    cp_hot = PropsSI("C", "T", hot_in.T, "P", hot_in.P, hot_in.fluid)
    cp_cold = PropsSI("C", "T", cold_in.T, "P", cold_in.P, cold_in.fluid)

    C_hot = hot_in.mdot * cp_hot
    C_cold = cold_in.mdot * cp_cold
    C_min = min(C_hot, C_cold)

    Q = effectiveness * C_min * (hot_in.T - cold_in.T)

    h_hot_out = hot_in.h - Q / hot_in.mdot
    h_cold_out = cold_in.h + Q / cold_in.mdot

    hot_out = Stream(
        state=state_from_Ph(hot_in.fluid, hot_in.P, h_hot_out),
        mdot=hot_in.mdot,
        fluid=hot_in.fluid,
    )
    cold_out = Stream(
        state=state_from_Ph(cold_in.fluid, cold_in.P, h_cold_out),
        mdot=cold_in.mdot,
        fluid=cold_in.fluid,
    )
    return hot_out, cold_out, Q
