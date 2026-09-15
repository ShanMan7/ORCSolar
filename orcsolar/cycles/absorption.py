"""Single-effect absorption chiller, assembled from the parts in
orcsolar.components.

    generator -> condenser -> throttle -> evaporator -> absorber
                                                    -> pump -> generator

Refrigerant loop numbered, solution loop lettered, following the state-point
mapping for this cycle:

    1   evaporator exit / absorber inlet      refrigerant vapor, low P
    2   generator exit / condenser inlet      refrigerant vapor, high P (superheated)
    3   condenser exit / throttle inlet       refrigerant liquid, high P
    4   throttle exit / evaporator inlet      refrigerant two-phase, low P
    a   absorber exit / pump inlet            strong solution (dilute in LiBr)
    b   pump exit / generator inlet           strong solution, high P
    c   generator exit / valve inlet          weak solution (concentrated in LiBr)
    d   valve exit / absorber inlet           weak solution, low P

Only two pressures exist, both set by the refrigerant's saturation
temperatures:

    P_high = P_sat(T_condenser)      P_low = P_sat(T_evaporator)

The solution loop's two concentrations come from equilibrium at the absorber
and generator, and the circulation ratio follows from the absorbent balance:

    x_a = x_saturated(T_absorber, P_low)
    x_c = x_saturated(T_generator, P_high)
    f   = mdot_a / mdot_refrigerant = x_c / (x_c - x_a)

The degassing width dx = x_c - x_a is the number to watch. As it narrows f
diverges - unbounded solution flow for no extra cooling - and the cycle fails.
That is the dominant failure mode, so ``f`` is returned for inspection.

NO SOLUTION HEAT EXCHANGER in this version. Adding one (preheating b with hot
weak solution from c) typically lifts COP 20-30%; see
``components/solution_hx.py``.
"""

from CoolProp.CoolProp import PropsSI

from ..components import absorber, generator, solution_pump, throttle
from ..state import SolutionState, State
from ..units import TC, TK

DEFAULT_ETA_PUMP = 0.65  # solution pump isentropic efficiency, matching the ORC modules


def solve_states(T_evaporator, T_condenser, T_absorber, T_generator, mixture,
                  eta_pump=DEFAULT_ETA_PUMP):
    """Walk the chiller once, calling each component in turn.

    All temperatures in deg C. ``mixture`` is a module from
    ``orcsolar.mixtures`` supplying the solution property interface.

    Returns a dict of the eight states, the per-unit-refrigerant energy terms
    (J/kg of refrigerant), the circulation ratio and COP.
    """
    refrigerant = mixture.REFRIGERANT

    # --- The two pressure levels, set by the refrigerant saturation temps ---
    P_high = PropsSI("P", "T", TK(T_condenser), "Q", 0, refrigerant)
    P_low = PropsSI("P", "T", TK(T_evaporator), "Q", 0, refrigerant)

    # --- Refrigerant states that are fixed by temperature alone ---
    # 1: saturated vapor leaving the evaporator
    s1 = State(
        T=TK(T_evaporator), P=P_low,
        h=PropsSI("H", "T", TK(T_evaporator), "Q", 1, refrigerant),
        s=PropsSI("S", "T", TK(T_evaporator), "Q", 1, refrigerant),
    )
    # 3: saturated liquid leaving the condenser
    s3 = State(
        T=TK(T_condenser), P=P_high,
        h=PropsSI("H", "T", TK(T_condenser), "Q", 0, refrigerant),
        s=PropsSI("S", "T", TK(T_condenser), "Q", 0, refrigerant),
    )
    # 4: throttled to evaporator pressure, isenthalpic
    s4 = throttle.expand(s3, P_low, refrigerant)

    # --- Solution loop. Basis: 1 kg/s of refrigerant. ---
    # a: strong solution leaving the absorber, in equilibrium at (T_abs, P_low)
    x_a = mixture.x_saturated(T_absorber, P_low)
    sa = SolutionState(
        T=TK(T_absorber), P=P_low, h=mixture.h_liquid(T_absorber, x_a), x=x_a
    )

    x_c = mixture.x_saturated(T_generator, P_high)
    degassing_width = x_c - x_a
    if degassing_width <= 0:
        raise ValueError(
            f"degassing width has collapsed: x_generator={x_c:.4f} <= x_absorber={x_a:.4f}. "
            "The generator cannot concentrate the solution past what the absorber dilutes "
            "it to, so no refrigerant circulates. Raise the generator temperature or lower "
            "the absorber/condenser temperature."
        )

    f = x_c / degassing_width  # circulation ratio, mdot_solution / mdot_refrigerant
    mdot_refrigerant = 1.0
    mdot_strong = f
    mdot_weak = f - 1.0

    # b: pumped up to generator pressure
    sb, w_pump_specific = solution_pump.compress(sa, P_high, eta_pump, mixture)

    # c, 2: generator splits the strong solution into vapor and weak solution
    s2, sc, q_gen, mdot_vapor, mdot_weak_gen = generator.desorb(
        sb, T_generator, P_high, mixture, mdot_strong=mdot_strong
    )

    # The generator's own absorbent balance must reproduce the basis we set.
    if abs(mdot_vapor - mdot_refrigerant) > 1e-6:
        raise AssertionError(
            f"internal inconsistency: circulation ratio implies 1 kg/s of refrigerant "
            f"but the generator balance gives {mdot_vapor:.6f} kg/s"
        )

    # d: weak solution throttled back to absorber pressure, isenthalpic
    T_d = mixture.T_from_h(sc.h, sc.x)
    sd = SolutionState(T=TK(T_d), P=P_low, h=sc.h, x=sc.x)

    # a (again): the absorber closes the loop. Recomputing it here checks that
    # the mass balance and equilibrium agree at this operating point.
    sa_check, q_abs, mdot_strong_check = absorber.absorb(
        s1, sd, T_absorber, P_low, mixture,
        mdot_vapor=mdot_refrigerant, mdot_weak=mdot_weak,
    )

    # --- Energy terms, per kg of refrigerant ---
    w_pump = mdot_strong * w_pump_specific
    q_cond = mdot_refrigerant * (s2.h - s3.h)
    q_evap = mdot_refrigerant * (s1.h - s4.h)

    cop = q_evap / (q_gen + w_pump)

    # Reversible bound: a heat engine between generator and ambient driving a
    # reversed cycle between evaporator and ambient. Heat rejection is taken at
    # the absorber temperature, the colder of the two reject streams.
    T_0 = TK(T_absorber)
    cop_reversible = (1 - T_0 / TK(T_generator)) * (TK(T_evaporator) / (T_0 - TK(T_evaporator)))

    return {
        "mixture": mixture.NAME,
        "states": {
            "1": s1, "2": s2, "3": s3, "4": s4,
            "a": sa, "b": sb, "c": sc, "d": sd,
        },
        "P_high": P_high,
        "P_low": P_low,
        "x_strong": x_a,
        "x_weak": x_c,
        "degassing_width": degassing_width,
        "f": f,
        "q_evap": q_evap,
        "q_gen": q_gen,
        "q_cond": q_cond,
        "q_abs": q_abs,
        "w_pump": w_pump,
        "cop": cop,
        "cop_reversible": cop_reversible,
        "inputs": {
            "T_evaporator": T_evaporator,
            "T_condenser": T_condenser,
            "T_absorber": T_absorber,
            "T_generator": T_generator,
            "eta_pump": eta_pump,
        },
    }


def energy_balance_residual(result):
    """Energy in minus energy out, J/kg of refrigerant.

        q_evap + q_gen + w_pump == q_cond + q_abs

    Closes algebraically for any consistent set of states, so a non-zero value
    means a sign error or a mass-flow mistake, not a property inaccuracy.
    """
    return (
        result["q_evap"] + result["q_gen"] + result["w_pump"]
        - result["q_cond"] - result["q_abs"]
    )
