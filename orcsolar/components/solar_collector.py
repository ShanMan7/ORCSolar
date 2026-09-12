"""Solar collector field.

STUB - not implemented. Supply the equation and coefficients to fill in.

The one thing that must not be simplified away here: collector efficiency
**falls as inlet temperature rises**, because thermal losses scale with the
gap between absorber and ambient. In this system the collector inlet is data
center waste heat (~45-65 C) rather than ambient water, so the collector runs
hotter and less efficiently than a standalone solar field would. A
constant-efficiency collector model would hide that trade-off entirely and
make waste-heat preheating look free.

Expected form (standard EN 12975 / ASHRAE 93 quadratic):

    dT = T_mean - T_ambient          where T_mean = (T_in + T_out) / 2
    eta = eta_0 - a1*dT/G - a2*dT^2/G
    Q_useful = eta * A * G

    G: global/direct irradiance on the collector plane, W/m^2
    A: aperture area, m^2
    eta_0, a1 [W/m^2-K], a2 [W/m^2-K^2]: from the collector datasheet

Because T_mean depends on T_out, which depends on Q, this is implicit - either
iterate to convergence or solve the resulting quadratic directly.

Representative coefficients, for orientation only (confirm against the actual
collector before using): flat plate eta_0~0.75, a1~3.5, a2~0.015; evacuated
tube eta_0~0.72, a1~1.5, a2~0.008. At dT=120 K and G=800 W/m^2 the flat-plate
curve goes negative - i.e. that technology physically cannot reach the
high-temperature regime, which is why collector type and target temperature
have to be chosen together.
"""


def outlet_stream(inlet, irradiance, T_ambient_celsius, area, eta_0, a1, a2):
    """Heat ``inlet`` through the collector field. Returns ``(outlet, Q_useful)``.

    See module docstring for the efficiency curve to implement.
    """
    raise NotImplementedError(
        "Solar collector efficiency curve not implemented. See the module "
        "docstring for the required form and the implicit-T_mean caveat."
    )
