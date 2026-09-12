"""Absorption chiller absorber.

STUB - not implemented. Governing equations below; the missing piece is the
mixture property model (see ``orcsolar.mixtures``).

Refrigerant vapor leaving the evaporator dissolves into weak solution
returning from the generator, producing strong solution for the pump. The
process is exothermic - dissolution releases the heat of solution on top of
the latent heat - so the absorber rejects heat to ambient and its temperature
is what sets the low-side concentration.

Using the cycle diagram's labels - 1 = refrigerant vapor in, d = weak solution
in, a = strong solution out:

    Total mass:    mdot_d + mdot_1 = mdot_a
    Species mass:  mdot_d*x_d + mdot_1*x_1 = mdot_a*x_a
    Energy:        Q_abs = mdot_1*h_1 + mdot_d*h_d - mdot_a*h_a

Per unit refrigerant flow, with f = mdot_a / mdot_r:

    q_abs = h_1 + (f - 1)*h_d - f*h_a

Closure assumes the strong solution leaves saturated at absorber conditions:

    x_a = x_saturated(T_absorber, P_low)

Note this makes absorber temperature a first-order design variable, not a
detail: it is half of the degassing width dx = x_a - x_c, so rejecting heat to
a warmer ambient narrows dx and degrades COP sharply. That coupling is why the
heat-rejection block (``heat_rejection.py``) has to be modeled rather than
assumed constant.
"""


def absorb(vapor_in, weak_in, T_absorber_celsius, P_low, mixture):
    """Dissolve refrigerant vapor into the weak solution.

    Returns ``(strong_out, Q_abs)``. See module docstring.
    """
    raise NotImplementedError(
        "Absorber not implemented - needs a mixture property model for "
        "x_saturated(T, P) and h(T, x). See orcsolar.mixtures."
    )
