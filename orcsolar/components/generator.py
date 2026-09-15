"""Absorption chiller generator (desorber).

Heat driven in at the generator temperature boils refrigerant out of the
strong solution arriving from the pump, leaving weak (concentrated) solution
behind. Using the cycle diagram's labels - b = strong solution in, 2 =
refrigerant vapor out, c = weak solution out:

    Total mass:    mdot_b = mdot_2 + mdot_c
    Species mass:  mdot_b*x_b = mdot_c*x_c       (absorbent leaves only as liquid)
    Energy:        Q_g = mdot_2*h_2 + mdot_c*h_c - mdot_b*h_b

The species balance is written on the **absorbent** (LiBr), which is
non-volatile and therefore stays entirely in the liquid - that is what makes
LiBr-H2O simpler than NH3-H2O, where the absorbent is volatile, the vapor is
not pure, and a rectifier is needed.

Closure comes from assuming the weak solution leaves in equilibrium with the
vapor at generator conditions:

    x_c = x_saturated(T_generator, P_high)

The vapor leaves at generator temperature, not condenser temperature, so it is
superheated relative to the condenser - state 2 is a superheated-vapor state
and h_2 must be evaluated at (T_generator, P_high), not as saturated vapor.
"""

from CoolProp.CoolProp import PropsSI

from ..state import SolutionState, State
from ..units import TK


def desorb(strong_in, T_generator_celsius, P_high, mixture, mdot_strong=1.0):
    """Boil refrigerant out of the strong solution.

    Returns ``(vapor_out, weak_out, Q_gen, mdot_vapor, mdot_weak)``.
    Q_gen is in W if ``mdot_strong`` is in kg/s; on the default unit basis it
    is J per kg of solution entering.
    """
    x_c = mixture.x_saturated(T_generator_celsius, P_high)

    if x_c <= strong_in.x:
        raise ValueError(
            f"generator does not concentrate the solution: x_out={x_c:.4f} <= "
            f"x_in={strong_in.x:.4f}. The generator is too cold (or the condenser "
            "too hot) to drive any refrigerant off - there is no cycle."
        )

    mixture.check_crystallization(T_generator_celsius, x_c, label="generator outlet")
    mixture.check_fit_range(T_generator_celsius, x_c, label="generator outlet")

    # Absorbent balance sets the split: all LiBr entering leaves as liquid.
    mdot_weak = mdot_strong * strong_in.x / x_c
    mdot_vapor = mdot_strong - mdot_weak

    weak_out = SolutionState(
        T=TK(T_generator_celsius),
        P=P_high,
        h=mixture.h_liquid(T_generator_celsius, x_c),
        x=x_c,
    )

    # Refrigerant vapor, superheated: it leaves at generator temperature but
    # at the condenser's pressure.
    T_vapor = TK(T_generator_celsius)
    vapor_out = State(
        T=T_vapor,
        P=P_high,
        h=PropsSI("H", "T", T_vapor, "P", P_high, mixture.REFRIGERANT),
        s=PropsSI("S", "T", T_vapor, "P", P_high, mixture.REFRIGERANT),
    )

    Q_gen = mdot_vapor * vapor_out.h + mdot_weak * weak_out.h - mdot_strong * strong_in.h

    return vapor_out, weak_out, Q_gen, mdot_vapor, mdot_weak
