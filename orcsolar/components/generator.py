"""Absorption chiller generator (desorber).

STUB - not implemented. The governing equations are written out below; what is
missing is the mixture property model they call (see ``orcsolar.mixtures``).

Heat driven in at T_generator boils refrigerant vapor out of the strong
solution arriving from the pump, leaving weak solution behind. Using the state
labels from the cycle diagram - b = strong solution in, 2 = refrigerant vapor
out, c = weak solution out:

    Total mass:    mdot_b = mdot_2 + mdot_c
    Species mass:  mdot_b*x_b = mdot_2*x_2 + mdot_c*x_c
    Energy:        Q_gen = mdot_2*h_2 + mdot_c*h_c - mdot_b*h_b

Per unit refrigerant flow, with the circulation ratio f = mdot_b / mdot_r:

    f = (x_2 - x_c) / (x_a - x_c)          ~ (1 - x_c)/(x_a - x_c) for pure vapor
    q_gen = h_2 + (f - 1)*h_c - f*h_b

Closure comes from assuming the weak solution leaves saturated at generator
conditions:

    x_c = x_saturated(T_generator, P_high)

The quantity to watch is the degassing width, dx = x_a - x_c. As it narrows f
diverges: enormous solution flow, no extra cooling, and the cycle fails. That
is the dominant failure mode of the whole chiller and the thing a parameter
sweep should be probing. Guard against small dx explicitly rather than letting
f quietly blow up.

For NH3-H2O the vapor is not pure - water is volatile and comes off with the
ammonia, so either a rectifier is modeled or x_2 is assumed ~0.999 and the
assumption noted. For LiBr-H2O the absorbent is non-volatile, the vapor is pure
water, and x_2 = 1 exactly.
"""


def desorb(strong_in, T_generator_celsius, P_high, mixture):
    """Boil refrigerant out of the strong solution.

    Returns ``(vapor_out, weak_out, Q_gen)``. See module docstring.
    """
    raise NotImplementedError(
        "Generator not implemented - needs a mixture property model for "
        "x_saturated(T, P) and h(T, x). See orcsolar.mixtures."
    )
