"""Thermodynamic state point shared by every component module.

The original notebooks tracked each state point as four loose same-shaped
variables (e.g. ``T1, P1, h1, s1``, then ``T2, P2, h2a, s2``, ...) repeated by
hand for every state in every cycle. Bundling them into one small object is
what lets each component file below expose a clean
``component_function(state_in, ...) -> state_out`` signature instead of a
long, position-sensitive argument list.
"""

from dataclasses import dataclass


@dataclass
class State:
    """A single thermodynamic state point of the working fluid.

    T: temperature, Kelvin
    P: pressure, Pa
    h: specific enthalpy, J/kg
    s: specific entropy, J/kg-K

    All SI, matching what CoolProp's ``PropsSI`` (the high-level, unit-fixed
    interface) always returns.
    """

    T: float
    P: float
    h: float
    s: float
