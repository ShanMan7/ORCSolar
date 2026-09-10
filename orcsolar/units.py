"""Temperature unit conversions between Celsius and Kelvin.

Kept under the same names (``TC``/``TK``) used throughout the original
notebooks, since every other module was rewritten to call them by these
names. Convention used everywhere else in this package: a
:class:`~orcsolar.state.State`'s ``T`` field is always Kelvin (CoolProp's
native SI unit); Celsius only ever appears at the edges - user-facing
function arguments (e.g. ``T1`` in degrees C) and plot labels.
"""


def TC(T):
    """Convert a temperature from Kelvin to Celsius."""
    return T - 273.15


def TK(T):
    """Convert a temperature from Celsius to Kelvin."""
    return T + 273.15
