"""Throttling (expansion) valve.

Both valves in an absorption chiller are throttles: the refrigerant valve
between condenser and evaporator, and the solution valve returning weak
solution from the generator to the absorber.

A throttle is adiabatic and does no work, so it is isenthalpic:

    h_out = h_in

That is a definition rather than a correlation, so it is implemented rather
than stubbed. Note the state still changes - pressure drops, temperature
usually drops, and entropy always rises (it is irreversible).
"""

from ..state import Stream, state_from_Ph


def expand(state_in, P_out, fluid):
    """Throttle a State down to ``P_out``. Returns the outlet State."""
    if P_out > state_in.P:
        raise ValueError(
            f"a throttle cannot raise pressure: P_out={P_out:.0f} Pa "
            f"> P_in={state_in.P:.0f} Pa"
        )
    return state_from_Ph(fluid, P_out, state_in.h)


def expand_stream(stream, P_out):
    """Throttle a Stream down to ``P_out``. Mass flow is unchanged."""
    return Stream(
        state=expand(stream.state, P_out, stream.fluid),
        mdot=stream.mdot,
        fluid=stream.fluid,
    )
