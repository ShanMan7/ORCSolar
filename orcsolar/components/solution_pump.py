"""Solution pump - raises strong solution from absorber to generator pressure.

Separate from ``pump.py`` because that one asks CoolProp for the properties of
a pure fluid, and a solution's properties come from a mixture model keyed on
concentration as well as temperature.

This is the only work input to the chiller, and it is tiny - pumping a liquid
across a few kPa. That is the whole trick of an absorption machine: it moves
the refrigerant from low to high pressure as a *liquid* rather than
compressing a vapor, which is why heat can substitute for work.

    W_p = mdot_a * (h_b - h_a)  ~  mdot_a * v_a * (P_gen - P_abs)
"""

from ..state import SolutionState


def compress(state_in, P_out, eta_isentropic, mixture):
    """Pump solution from ``state_in`` up to ``P_out``.

    Returns ``(state_out, work)`` with work the specific work consumed, J/kg,
    positive - matching the sign convention in ``pump.py``.

    Concentration is unchanged; the pump moves solution, it does not separate
    it. The v*dP estimate is used rather than an entropy-based one because
    solution entropy is not available on a consistent datum (see
    ``SolutionState``), and for a nearly incompressible liquid the two agree
    closely anyway.
    """
    if P_out < state_in.P:
        raise ValueError(
            f"a pump cannot lower pressure: P_out={P_out:.1f} Pa < P_in={state_in.P:.1f} Pa"
        )

    T_in_celsius = state_in.T - 273.15
    v = 1.0 / mixture.rho_liquid(T_in_celsius, state_in.x)

    work = v * (P_out - state_in.P) / eta_isentropic
    h_out = state_in.h + work

    T_out_celsius = mixture.T_from_h(h_out, state_in.x)
    state_out = SolutionState(
        T=T_out_celsius + 273.15,
        P=P_out,
        h=h_out,
        x=state_in.x,
    )
    return state_out, work
