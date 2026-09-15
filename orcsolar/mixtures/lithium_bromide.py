"""LiBr-H2O mixture properties.

Split source, for the reasons recorded in ``orcsolar/mixtures/__init__.py``:

  - ``P_saturated`` wraps CoolProp (``INCOMP::LiBr``), which reproduces the
    Duehring chart to ~1.5%.
  - ``h_liquid`` uses the ASHRAE correlation, because CoolProp's LiBr enthalpy
    carries no heat of solution - and the absorber and generator balances are
    made of precisely that term.
  - ``cp_liquid`` wraps CoolProp, which is reliable.

CONCENTRATION CONVENTION: ``x`` is the mass fraction of **LiBr** (the
absorbent), matching CoolProp's ``INCOMP::LiBr[x]`` syntax. So, in the
terminology of the cycle diagram:

    strong solution (rich in refrigerant, dilute in LiBr) -> LOW x   (state a)
    weak solution  (lean in refrigerant, concentrated LiBr) -> HIGH x (state c)

Note some LiBr literature uses "strong" to mean strong *in LiBr*, i.e. the
exact opposite. This module follows the cycle diagram's sense throughout.

ENTHALPY DATUM: the ASHRAE correlation is referenced to h = 0 for saturated
liquid water at 0 C. IAPWS (CoolProp's ``'Water'``) references h = 0 at the
triple point, 0.01 C, where h_f = 0.0006 kJ/kg. The two agree to well under
1 J/kg, so solution enthalpies from here and refrigerant enthalpies from
CoolProp can be used in the same control-volume balance without correction.
This is the key reason for not using CoolProp's own LiBr enthalpy, which sits
on a per-concentration datum ~84 kJ/kg away from 'Water'.
"""

import warnings

from CoolProp.CoolProp import PropsSI
from scipy.optimize import brentq

from ..units import TK

NAME = "lithium-bromide-water"
REFRIGERANT = "Water"

# CoolProp's INCOMP::LiBr limits, probed empirically.
X_MAX = 0.75  # mass fraction LiBr
T_RANGE_K = (273.0, 500.0)

# ASHRAE Handbook - Fundamentals, solution enthalpy correlation.
#   h [kJ/kg] = A(X) + B(X)*t + C(X)*t^2
# with t in deg C and X the LiBr mass PERCENT (e.g. 60.0, not 0.60).
# Stated validity: roughly 15-165 C and 40-70% LiBr.
_A = (-2024.33, 163.309, -4.88161, 6.302948e-2, -2.913705e-4)
_B = (18.2829, -1.1691757, 3.248041e-2, -4.034184e-4, 1.8520569e-6)
_C = (-3.7008214e-2, 2.8877666e-3, -8.1313015e-5, 9.9116628e-7, -4.4441207e-9)

# Outside this band the ASHRAE fit is an extrapolation.
X_FIT_RANGE = (0.40, 0.70)
T_FIT_RANGE_C = (15.0, 165.0)

# Crystallization guard. The real solubility boundary is a curve in (T, x);
# this is a flat conservative threshold, NOT a correlation - see
# `check_crystallization`.
X_CRYSTALLIZATION_WARN = 0.65


def _poly(coeffs, X_percent):
    return sum(c * X_percent**n for n, c in enumerate(coeffs))


def h_liquid(T_celsius, x):
    """Solution specific enthalpy, J/kg, on the ASHRAE datum.

    Includes the heat of solution, which is the whole point - a correlation
    without it makes the absorber and generator balances meaningless.
    """
    X = x * 100.0
    h_kJ = _poly(_A, X) + _poly(_B, X) * T_celsius + _poly(_C, X) * T_celsius**2
    return h_kJ * 1000.0


def P_saturated(T_celsius, x):
    """Equilibrium water-vapor pressure over the solution, Pa.

    Wraps CoolProp, which handles this well. Queried at Q=0 rather than by
    pressure: at absorber and generator conditions the loop sits *at*
    saturation, so a pressure input trips "equations are valid for liquid
    phase only" on a few Pa of rounding.
    """
    if not 0.0 <= x <= X_MAX:
        raise ValueError(f"LiBr mass fraction {x:.4f} outside CoolProp range [0, {X_MAX}]")
    return PropsSI("P", "T", TK(T_celsius), "Q", 0, f"INCOMP::LiBr[{x}]")


def x_saturated(T_celsius, P):
    """Equilibrium LiBr mass fraction at (T, P), by inverting ``P_saturated``.

    Vapor pressure falls monotonically as LiBr concentration rises, so a
    bracketed root-find is safe. CoolProp cannot do this direction itself
    ("This pair of inputs [PQ_INPUTS] is not yet supported").
    """
    P_pure_water = P_saturated(T_celsius, 0.0)
    P_most_concentrated = P_saturated(T_celsius, X_MAX)

    if P > P_pure_water:
        raise ValueError(
            f"no solution: {P:.1f} Pa exceeds pure-water saturation pressure "
            f"{P_pure_water:.1f} Pa at {T_celsius:.1f} C. Physically this means the "
            "absorber/generator temperature is too high for this pressure level."
        )
    if P < P_most_concentrated:
        raise ValueError(
            f"no solution: {P:.1f} Pa is below the vapor pressure "
            f"{P_most_concentrated:.1f} Pa of the most concentrated solution CoolProp "
            f"models (x={X_MAX}) at {T_celsius:.1f} C."
        )

    return brentq(lambda x: P_saturated(T_celsius, x) - P, 0.0, X_MAX, xtol=1e-10)


def cp_liquid(T_celsius, x):
    """Solution specific heat, J/kg-K. CoolProp's value is reliable here."""
    return PropsSI("C", "T", TK(T_celsius), "Q", 0, f"INCOMP::LiBr[{x}]")


def rho_liquid(T_celsius, x):
    """Solution density, kg/m^3. Used for the pump's v*dP work term."""
    return PropsSI("D", "T", TK(T_celsius), "Q", 0, f"INCOMP::LiBr[{x}]")


def check_crystallization(T_celsius, x, label="solution"):
    """Warn if the solution is near the crystallization boundary.

    This is a **flat threshold, not a solubility correlation** - the true
    boundary is a curve in (T, x) and depends strongly on temperature. It is
    here because the property correlations return perfectly reasonable-looking
    numbers deep inside the forbidden region, so a sweep will silently report
    performance for a machine that has solidified. Replace with a real
    solubility curve before trusting any result near the limit.
    """
    if x > X_CRYSTALLIZATION_WARN:
        warnings.warn(
            f"{label}: LiBr mass fraction {x:.3f} at {T_celsius:.1f} C is above the "
            f"conservative crystallization threshold of {X_CRYSTALLIZATION_WARN}. "
            "This is a flat guard, not a real solubility curve - verify against one.",
            stacklevel=2,
        )


def check_fit_range(T_celsius, x, label="solution"):
    """Warn when the ASHRAE enthalpy fit is being extrapolated."""
    if not X_FIT_RANGE[0] <= x <= X_FIT_RANGE[1]:
        warnings.warn(
            f"{label}: x={x:.3f} outside the ASHRAE enthalpy fit range {X_FIT_RANGE}; "
            "h_liquid is extrapolating.",
            stacklevel=2,
        )
    if not T_FIT_RANGE_C[0] <= T_celsius <= T_FIT_RANGE_C[1]:
        warnings.warn(
            f"{label}: T={T_celsius:.1f} C outside the ASHRAE enthalpy fit range "
            f"{T_FIT_RANGE_C}; h_liquid is extrapolating.",
            stacklevel=2,
        )


def T_from_h(h, x, T_bounds_celsius=(0.0, 200.0)):
    """Invert ``h_liquid`` for temperature at fixed concentration, deg C.

    Needed downstream of the pump and the solution valve, where enthalpy is
    what the energy balance gives you and temperature is what you want to
    report. Enthalpy rises monotonically with temperature at fixed x, so a
    bracketed root-find is safe.
    """
    lo, hi = T_bounds_celsius
    return brentq(lambda T: h_liquid(T, x) - h, lo, hi, xtol=1e-9)
