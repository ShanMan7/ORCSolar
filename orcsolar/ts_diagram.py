"""Saturation dome - the backbone curve of a T-s diagram.

Consolidates the ``TsPlot(F)`` function that was copy-pasted (with drifted
resolution and return-units) into all three original notebooks: 100 pressure
points and Kelvin output in ORCModel (1).ipynb, 1000 points and Celsius
output in ORCModelReheat.ipynb. This version always returns Kelvin (SI, same
convention as :class:`~orcsolar.state.State`) and defaults to the
higher (1000-point) resolution; convert to Celsius at plot time if needed
(see ``orcsolar.units.TC``).
"""

import numpy as np
from CoolProp.CoolProp import PropsSI


def saturation_dome(fluid, n_points=1000):
    """Return ``(T_kelvin, s)`` arrays tracing the saturated-liquid branch
    then the saturated-vapor branch, suitable for plotting a T-s dome."""
    P_min = PropsSI("P_min", fluid)
    P_max = PropsSI("Pcrit", fluid)
    pressures = np.logspace(np.log10(P_min), np.log10(P_max), n_points)

    T_liquid, s_liquid, T_vapor, s_vapor = [], [], [], []
    for P in pressures:
        T_liquid.append(PropsSI("T", "P", P, "Q", 0, fluid))  # saturated liquid
        s_liquid.append(PropsSI("S", "P", P, "Q", 0, fluid))
        T_vapor.append(PropsSI("T", "P", P, "Q", 1, fluid))  # saturated vapor
        s_vapor.append(PropsSI("S", "P", P, "Q", 1, fluid))

    T_vapor = np.flip(np.array(T_vapor))
    s_vapor = np.flip(np.array(s_vapor))

    T_dome = np.append(np.array(T_liquid), T_vapor)
    s_dome = np.append(np.array(s_liquid), s_vapor)
    return T_dome, s_dome
