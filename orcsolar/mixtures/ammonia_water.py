"""NH3-H2O mixture properties.

STUB - not implemented. CoolProp supplies nothing here (see the package
docstring in ``orcsolar/mixtures/__init__.py``), so all five functions need a
correlation. The standard source is Patek & Klomfar, "Simple functions for
fast calculations of selected thermodynamic properties of the ammonia-water
system", Int. J. Refrigeration 18(4), 1995.

Conventions for this package:
  - ``x`` is the **mass** fraction of NH3 in the liquid, matching the
    absorption-chiller literature. CoolProp's mixture syntax uses *mole*
    fractions, so convert at the boundary if the two ever meet:
    M(NH3) = 0.01703 kg/mol, M(H2O) = 0.018015 kg/mol; mass 0.50 -> mole 0.5141.
  - Temperatures in deg C at the interface, pressures in Pa, enthalpies J/kg,
    matching the rest of the package.

Characteristics that matter for the cycle: ammonia is the refrigerant and
water the absorbent, and because **water is volatile** the vapor leaving the
generator is not pure - it carries water that would raise the evaporator
temperature and degrade capacity. Real machines fit a rectifier; a first model
usually assumes x_vapor ~ 0.999 and notes the assumption. This pair can chill
below 0 C, which LiBr-H2O cannot.
"""

NAME = "ammonia-water"
REFRIGERANT = "Ammonia"
M_NH3 = 0.01703  # kg/mol
M_H2O = 0.018015  # kg/mol


def x_saturated(T_celsius, P):
    """Equilibrium liquid NH3 mass fraction at (T, P). Needs a root-find on
    ``P_saturated``."""
    raise NotImplementedError("NH3-H2O x_saturated not implemented (Patek-Klomfar 1995).")


def P_saturated(T_celsius, x):
    """Bubble pressure, Pa, of a solution at mass fraction ``x``."""
    raise NotImplementedError("NH3-H2O P_saturated not implemented (Patek-Klomfar 1995).")


def h_liquid(T_celsius, x):
    """Solution specific enthalpy, J/kg. Must include the heat of mixing."""
    raise NotImplementedError("NH3-H2O h_liquid not implemented (Patek-Klomfar 1995).")


def h_vapor(T_celsius, P, x):
    """Specific enthalpy, J/kg, of vapor in equilibrium with the solution."""
    raise NotImplementedError("NH3-H2O h_vapor not implemented (Patek-Klomfar 1995).")


def cp_liquid(T_celsius, x):
    """Solution specific heat, J/kg-K."""
    raise NotImplementedError("NH3-H2O cp_liquid not implemented (Patek-Klomfar 1995).")
