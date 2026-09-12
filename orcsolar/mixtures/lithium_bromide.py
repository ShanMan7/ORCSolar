"""LiBr-H2O mixture properties.

PARTIAL STUB. Unlike NH3-H2O, CoolProp does cover part of this pair - see the
package docstring in ``orcsolar/mixtures/__init__.py`` for the evidence:

  - VLE, density, cp, viscosity: available and accurate via
    ``'INCOMP::LiBr[x]'``. ``P_saturated`` below can wrap CoolProp directly.
  - Enthalpy: **not usable** - CoolProp's LiBr enthalpy has no heat of
    solution (heat of dilution comes back as ~0.4 J/kg where reality is
    -30 to -50 kJ/kg) and sits on a different datum from ``'Water'``. So
    ``h_liquid`` needs a real correlation: Patek & Klomfar (2006), or the
    ASHRAE Handbook - Fundamentals formulation.

Conventions: ``x`` is the **mass fraction of LiBr** (the absorbent), which is
how this pair is conventionally reported - note that is the opposite sense to
``ammonia_water.x``, where x is the refrigerant. Keep the two straight when
writing the shared cycle solver.

CoolProp limits to respect: x in [0, 0.75], T in [273, 500] K. Practical
gotcha - at absorber and generator conditions the loop sits *at* saturation, so
query with ``Q=0`` rather than passing P, or a few Pa of rounding will trip
"equations are valid for liquid phase only".

Characteristics that matter for the cycle: the absorbent is non-volatile, so
the vapor is pure water and **no rectifier is needed** - x_vapor = 1 exactly.
The costs are that the refrigerant is water, so the evaporator cannot go below
~4 C (air conditioning, not refrigeration), and that concentrated solution
**crystallizes** at high x and low temperature. That crystallization boundary
is a hard operating limit and should be checked explicitly in any sweep, since
the equations will happily return numbers well inside the forbidden region.
"""

NAME = "lithium-bromide-water"
REFRIGERANT = "Water"

COOLPROP_MAX_X = 0.75  # mass fraction LiBr
COOLPROP_T_RANGE_K = (273.0, 500.0)


def x_saturated(T_celsius, P):
    """Equilibrium LiBr mass fraction at (T, P). Invert ``P_saturated``
    numerically - it is monotonic, so ``scipy.optimize.brentq`` is enough.
    CoolProp does not support the reverse direction directly ("This pair of
    inputs [PQ_INPUTS] is not yet supported")."""
    raise NotImplementedError("LiBr x_saturated not implemented - invert P_saturated.")


def P_saturated(T_celsius, x):
    """Equilibrium water-vapor pressure over the solution, Pa.

    Can wrap CoolProp directly - this is the part that works:
        PropsSI('P', 'T', TK(T_celsius), 'Q', 0, f'INCOMP::LiBr[{x}]')
    """
    raise NotImplementedError("LiBr P_saturated not implemented - wrap CoolProp INCOMP::LiBr.")


def h_liquid(T_celsius, x):
    """Solution specific enthalpy, J/kg.

    Do NOT wrap CoolProp here - its LiBr enthalpy omits the heat of solution,
    which is the term the absorber and generator balances are made of. Use
    Patek-Klomfar (2006) or ASHRAE, and state the datum explicitly.
    """
    raise NotImplementedError("LiBr h_liquid not implemented (Patek-Klomfar 2006 / ASHRAE).")


def cp_liquid(T_celsius, x):
    """Solution specific heat, J/kg-K. CoolProp's value is usable."""
    raise NotImplementedError("LiBr cp_liquid not implemented - can wrap CoolProp.")


def crystallization_x(T_celsius):
    """Maximum LiBr mass fraction before crystallization at this temperature.

    A hard operating boundary with no thermodynamic warning attached - the
    property correlations return perfectly reasonable-looking values past it.
    Worth implementing alongside the rest so sweeps can be masked.
    """
    raise NotImplementedError("LiBr crystallization limit not implemented.")
