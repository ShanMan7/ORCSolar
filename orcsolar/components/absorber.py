"""Absorption chiller absorber.

Refrigerant vapor leaving the evaporator dissolves into weak solution
returning from the generator, producing strong solution for the pump. The
process is exothermic - dissolution releases the heat of solution on top of
the latent heat - so the absorber rejects heat, and its temperature sets the
low-side concentration.

Using the cycle diagram's labels - 1 = refrigerant vapor in, d = weak solution
in, a = strong solution out:

    Total mass:    mdot_a = mdot_1 + mdot_d
    Species mass:  mdot_d*x_d = mdot_a*x_a      (absorbent is non-volatile)
    Energy:        Q_a = mdot_1*h_1 + mdot_d*h_d - mdot_a*h_a

Two things fix x_a - the mass balance above, and equilibrium at absorber
conditions, x_a = x_saturated(T_absorber, P_low). A converged cycle has to
satisfy both, so this component computes x_a from the mass balance and checks
it against equilibrium, which catches an inconsistent set of inputs rather
than quietly returning a number.

Absorber temperature is a first-order design variable, not a detail: it is one
end of the degassing width dx = x_c - x_a, so rejecting heat to a warmer
ambient narrows dx and degrades COP sharply.
"""

from ..state import SolutionState
from ..units import TK


def absorb(vapor_in, weak_in, T_absorber_celsius, P_low, mixture,
           mdot_vapor=1.0, mdot_weak=None, equilibrium_rtol=1e-4):
    """Dissolve refrigerant vapor into the returning weak solution.

    Returns ``(strong_out, Q_abs, mdot_strong)``.

    ``mdot_weak`` defaults to the value implied by the absorbent balance with
    equilibrium composition, which is the usual design-point closure.
    """
    x_a = mixture.x_saturated(T_absorber_celsius, P_low)

    if x_a >= weak_in.x:
        raise ValueError(
            f"absorber cannot dilute the solution: x_out={x_a:.4f} >= x_in={weak_in.x:.4f}. "
            "The absorber is too hot (or the evaporator too cold) to take up vapor."
        )

    mixture.check_fit_range(T_absorber_celsius, x_a, label="absorber outlet")

    if mdot_weak is None:
        # Absorbent balance: mdot_d*x_d = mdot_a*x_a = (mdot_1 + mdot_d)*x_a
        mdot_weak = mdot_vapor * x_a / (weak_in.x - x_a)
    else:
        mdot_strong_check = mdot_vapor + mdot_weak
        x_a_from_balance = mdot_weak * weak_in.x / mdot_strong_check
        if abs(x_a_from_balance - x_a) > equilibrium_rtol * x_a:
            raise ValueError(
                f"absorber is inconsistent: the absorbent balance gives "
                f"x_a={x_a_from_balance:.5f} but equilibrium at {T_absorber_celsius:.1f} C "
                f"and {P_low:.1f} Pa requires x_a={x_a:.5f}. The supplied mass flows do "
                "not correspond to this operating point."
            )

    mdot_strong = mdot_vapor + mdot_weak

    strong_out = SolutionState(
        T=TK(T_absorber_celsius),
        P=P_low,
        h=mixture.h_liquid(T_absorber_celsius, x_a),
        x=x_a,
    )

    Q_abs = mdot_vapor * vapor_in.h + mdot_weak * weak_in.h - mdot_strong * strong_out.h

    return strong_out, Q_abs, mdot_strong
