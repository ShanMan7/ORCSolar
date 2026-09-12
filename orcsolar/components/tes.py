"""Thermal energy storage tank.

STUB - not implemented. Supply the equation to fill in.

TES is the one block that does not fit the "give it a state, get a state back"
pattern the other components follow, because **it has memory**. A turbine's
outlet depends only on its inlet; a tank's outlet depends on its whole history.
That is why it gets its own shape here, and why it is the block that forces the
plant layer to own a time loop when the model eventually goes transient.

STEADY-STATE (what to build first): the tank is a fixed-temperature node.
Charging and discharging balance, T_t is either an input or solved so that
supply matches demand, and the tank's only real parameter is a standing loss.

    Q_loss = UA * (T_tank - T_ambient)

TRANSIENT (later): a fully-mixed tank integrates

    M*cp * dT_tank/dt = sum_i( mdot_i * cp * (T_i - T_tank) ) - UA*(T_tank - T_ambient)

    M: stored mass, kg;  UA: standing-loss coefficient, W/K

A stratified tank instead carries a temperature profile - usually a stack of
nodes each with the above equation plus inter-node conduction and the logic
that places an incoming stream at its buoyancy-matched height. Stratification
matters here: the diagram feeds the tank from two sources at different
temperatures (raw waste heat and solar-boosted water), and a fully-mixed model
would average them into one lukewarm temperature, understating what the ORC and
chiller actually see. Decide mixed vs stratified before building the plant loop
- it changes the tank's interface, not just its internals.
"""


def standing_loss(T_tank_celsius, T_ambient_celsius, UA):
    """Heat lost from the tank to its surroundings, W. See module docstring."""
    raise NotImplementedError("TES standing loss not implemented.")


def step(T_tank_celsius, inflows, outflow_mdot, dt, mass, UA, T_ambient_celsius):
    """Advance the tank temperature by ``dt`` seconds. Transient use only.

    See module docstring for the governing ODE, and decide fully-mixed vs
    stratified before implementing - they do not share an interface.
    """
    raise NotImplementedError("TES transient integration not implemented.")
