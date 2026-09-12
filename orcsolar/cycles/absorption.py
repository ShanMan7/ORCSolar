"""Single-effect absorption chiller, assembled from the parts in
orcsolar.components.

STUB - not implemented. The components it calls (absorber, generator,
solution_hx) and the mixture properties they need are stubs too.

Flow, following the same convention as the ORC cycle modules - refrigerant
loop numbered, solution loop lettered:

    generator -> condenser -> throttle -> evaporator -> absorber
                                                   -> pump -> [SHX] -> generator

    1   evaporator outlet / absorber inlet     refrigerant vapor, low P
    2   generator outlet / condenser inlet     refrigerant vapor, high P
    3   condenser outlet                       saturated liquid, high P
    4   throttle outlet / evaporator inlet     low P, h_4 = h_3
    a   absorber outlet / pump inlet           strong solution, low P
    b   pump outlet / generator inlet          strong solution, high P
    c   generator outlet / valve inlet         weak solution, high P
    d   valve outlet / absorber inlet          weak solution, low P, h_d = h_c

Only two pressures exist, set by the two saturated refrigerant states:

    P_high = P_sat(T_condenser)      P_low = P_sat(T_evaporator)

Per unit refrigerant flow, with circulation ratio f = (x_2 - x_c)/(x_a - x_c):

    q_gen  = h_2 + (f - 1)*h_c - f*h_b
    q_abs  = h_1 + (f - 1)*h_d - f*h_a
    q_cond = h_2 - h_3
    q_evap = h_1 - h_4
    w_pump = f*(h_b - h_a)  ~  f*v_a*(P_high - P_low)/eta_pump

    COP = q_evap / (q_gen + w_pump)

Two checks worth building in from the start, both cheap:

    q_evap + q_gen + w_pump == q_cond + q_abs        (closes algebraically)
    COP_reversible = (1 - T_0/T_gen) * (T_evap/(T_0 - T_evap))

The second is the absorption analogue of Carnot - a heat engine between
generator and ambient driving a reversed cycle between evaporator and ambient.
Real single-effect machines land around half of it (COP ~0.7 against ~1.4 at
T_gen 90 C, T_0 35 C, T_evap 5 C), so a result far outside that band means a
bug, not a discovery.

The first version is intended without the solution heat exchanger - just the
eight states above. Add SHX afterwards and expect COP to rise 20-30%.
"""

DEFAULT_ETA_PUMP = 0.65  # solution pump isentropic efficiency, matching the ORC modules


def solve_states(T_evaporator, T_condenser, T_absorber, T_generator, mixture,
                  eta_pump=DEFAULT_ETA_PUMP):
    """Walk the chiller once, calling each component in turn.

    Temperatures in deg C. ``mixture`` is a module from ``orcsolar.mixtures``
    providing the solution property interface.

    Intended to return a dict shaped like the ORC cycles' - states plus
    per-unit-mass energy terms - with ``cop`` in place of ``eta`` and the
    circulation ratio ``f`` included, since it is the number that reveals a
    collapsing degassing width.
    """
    raise NotImplementedError(
        "Absorption cycle not implemented - needs absorber, generator and a "
        "mixture property model. See the module docstring for the equations."
    )
