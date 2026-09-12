"""Data center as a heat source (and a cooling load).

STUB - not implemented. Supply the equation to fill in.

This block appears twice in the system diagram and it is easy to model only
half of it: it *emits* waste heat into the recovery loop, and it *consumes*
the chilled water the absorption chiller produces. Those two are coupled - the
cooling you deliver becomes part of the heat you recover - so the loop has to
be closed honestly or the model will manufacture free cooling.

Expected form, waste-heat side:

    Q_waste = f_recoverable * P_IT
    Q_waste = mdot * cp * (T_dw - T_c)        (sets the loop's return temp)

    P_IT: IT power draw, W - essentially all of it becomes heat
    f_recoverable: fraction actually capturable by the coolant loop. This is a
        real modeling choice, not a constant: direct-to-chip liquid cooling
        captures most of it, air cooling much less, and the remainder escapes
        to the room and still has to be removed.

Temperature is the binding constraint on the whole system. Typical coolant
return temperatures: air-cooled 35-45 C, direct liquid cooling 45-65 C,
immersion ~50-60 C. None of these is hot enough on its own to drive a
single-effect absorption chiller (needs ~80 C+ at the generator) or to run an
ORC at a worthwhile efficiency - which is what the solar field is there to fix.
The waste heat's role is preheating, and its value should be judged that way.
"""


def waste_heat_stream(P_IT, f_recoverable, T_supply_celsius, T_return_celsius):
    """Waste-heat stream leaving the data center. Returns ``(stream, Q_waste)``.

    See module docstring for the form to implement.
    """
    raise NotImplementedError("Data center waste-heat model not implemented.")


def cooling_demand(P_IT, f_recoverable):
    """Cooling load the chilled-water loop must satisfy, W.

    Must be consistent with ``waste_heat_stream`` - the heat removed and the
    heat recovered are two views of the same energy.
    """
    raise NotImplementedError("Data center cooling demand not implemented.")
