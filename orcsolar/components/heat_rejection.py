"""Heat rejection to ambient - cooling tower or dry cooler.

STUB - not implemented. Supply the equation to fill in.

This block is *absent from the system diagram* but the system cannot work
without it. Both the ORC condenser and the absorption chiller reject heat to
ambient, and for the chiller that is a large flow - roughly Q_evaporator +
Q_generator leaves through the absorber and condenser combined, so the reject
loop moves more heat than the cooling it delivers.

Modeling it explicitly is what keeps the plant honest. If chiller and ORC heat
is allowed to disappear, or worse, to flow back toward the data center, the
model will close its energy balance while quietly breaking the second law.

Expected form (wet cooling tower):

    T_out = T_wetbulb + approach
    Q_rejected = mdot * cp * (T_in - T_out)

    approach: how close to wet-bulb the tower gets, K - 3-7 K typical
    T_wetbulb: from ambient dry-bulb and relative humidity

For a dry cooler, substitute dry-bulb for wet-bulb and expect a larger
approach. Either way the ambient condition sets the floor on condenser and
absorber temperature, which feeds straight back into ORC efficiency and
chiller COP - so this block couples the weather to the performance of
everything else, and shouldn't be a fixed 35 C once the model goes transient.
"""


def reject(inlet, T_ambient_celsius, approach, relative_humidity=None):
    """Cool ``inlet`` toward ambient. Returns ``(outlet, Q_rejected)``.

    See module docstring for the form to implement, and decide wet vs dry
    before implementing - they differ in which ambient temperature sets the
    floor.
    """
    raise NotImplementedError("Heat rejection model not implemented.")
