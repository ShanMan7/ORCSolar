"""Flow junctions: splitting one stream into several, merging several into one.

The "Flow Control" box in the system diagram is a splitter (waste heat divided
between the solar field and the TES); every return line that rejoins is a
mixer. Both are pure conservation - no property model, no correlation, nothing
to calibrate - so they are implemented here rather than stubbed.
"""

from ..state import Stream, state_from_Ph


def split(stream, fractions):
    """Divide ``stream`` into parallel streams carrying ``fractions`` of the flow.

    The thermodynamic state is unchanged by splitting - each branch leaves at
    the same T, P, h, s and only the mass flow differs.

    fractions: iterable summing to 1.0 (e.g. ``[0.3, 0.7]``)
    Returns a list of Streams, one per fraction.
    """
    total = sum(fractions)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"split fractions must sum to 1.0, got {total}")

    return [
        Stream(state=stream.state, mdot=stream.mdot * f, fluid=stream.fluid)
        for f in fractions
    ]


def mix(streams):
    """Adiabatically merge streams of the same fluid into one.

        mdot_out = sum(mdot_i)
        h_out    = sum(mdot_i * h_i) / mdot_out      (energy conservation)
        P_out    = min(P_i)

    Taking the lowest inlet pressure is the conservative choice: streams at
    different pressures cannot actually merge without the higher one throttling
    down to meet the lower.
    """
    streams = list(streams)
    if not streams:
        raise ValueError("mix() needs at least one stream")

    fluids = {s.fluid for s in streams}
    if len(fluids) > 1:
        raise ValueError(
            f"cannot mix different fluids: {sorted(fluids)}. Streams of "
            "different fluids meet across a heat exchanger, not a junction."
        )

    fluid = streams[0].fluid
    mdot_out = sum(s.mdot for s in streams)
    if mdot_out <= 0:
        raise ValueError("total mass flow into mix() must be positive")

    h_out = sum(s.mdot * s.h for s in streams) / mdot_out
    P_out = min(s.P for s in streams)

    return Stream(state=state_from_Ph(fluid, P_out, h_out), mdot=mdot_out, fluid=fluid)
