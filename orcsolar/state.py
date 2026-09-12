"""Thermodynamic state points and flowing streams.

Two levels, deliberately kept separate:

``State`` is **intensive** - T, P, h, s of a fluid, with no notion of how much
of it there is. The component and cycle models in ``orcsolar.components`` and
``orcsolar.cycles`` work entirely in State and per-unit-mass terms (J/kg), so
a cycle's answer is independent of plant size.

``Stream`` is **extensive** - a State plus a mass flow rate and the identity
of the fluid carrying it. The plant layer (``orcsolar.plant``) needs this: you
cannot split a flow, mix two returns, or size a heat exchanger without knowing
kg/s, and a system with a water loop, an ORC working fluid and a chiller
solution loop needs each stream to carry its own fluid name rather than having
it passed alongside as a bare string.

The bridge between the two levels is mass flow: a cycle reports q_in in J/kg,
the plant divides the available heat in W by it to get the kg/s the cycle can
actually support.
"""

from dataclasses import dataclass

from CoolProp.CoolProp import PropsSI

from .units import TK


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


@dataclass
class Stream:
    """A flowing quantity of a named fluid: a ``State``, plus how much and what.

    mdot: mass flow rate, kg/s
    fluid: CoolProp fluid name (or a mixture model's name, for the chiller
        solution loops where CoolProp cannot supply properties)

    T/P/h/s are exposed as passthrough properties so a Stream can be read like
    a State where only the intensive values matter.
    """

    state: State
    mdot: float
    fluid: str

    @property
    def T(self):
        return self.state.T

    @property
    def P(self):
        return self.state.P

    @property
    def h(self):
        return self.state.h

    @property
    def s(self):
        return self.state.s

    @property
    def H(self):
        """Enthalpy flow rate, W. This is the quantity that balances at a
        junction or across a component - not specific enthalpy."""
        return self.mdot * self.state.h


def state_from_TP(fluid, T_celsius, P):
    """State of ``fluid`` at a temperature (deg C) and pressure (Pa)."""
    T = TK(T_celsius)
    return State(
        T=T,
        P=P,
        h=PropsSI("H", "T", T, "P", P, fluid),
        s=PropsSI("S", "T", T, "P", P, fluid),
    )


def state_from_Ph(fluid, P, h):
    """State of ``fluid`` from pressure (Pa) and specific enthalpy (J/kg).

    The natural constructor downstream of anything that conserves energy -
    throttles, mixers, heat exchangers - where h is what you know.
    """
    return State(
        T=PropsSI("T", "P", P, "H", h, fluid),
        P=P,
        h=h,
        s=PropsSI("S", "P", P, "H", h, fluid),
    )


def stream_from_TP(fluid, T_celsius, P, mdot):
    """Stream of ``fluid`` at a temperature (deg C), pressure (Pa), kg/s."""
    return Stream(state=state_from_TP(fluid, T_celsius, P), mdot=mdot, fluid=fluid)


def water_stream(T_celsius, mdot, P=101325.0):
    """Liquid-water stream - the working substance of every secondary loop in
    the system diagram (waste-heat, solar, storage, chilled and hot water)."""
    return stream_from_TP("Water", T_celsius, P, mdot)
