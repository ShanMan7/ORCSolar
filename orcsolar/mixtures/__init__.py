"""Binary mixture property models for the absorption chiller solution loops.

Why this package exists: **CoolProp cannot supply these properties**, which was
verified empirically rather than assumed. The findings, so nobody has to
rediscover them:

NH3-H2O - not available at all. Both the high-level and low-level interfaces
fail at construction:

    Could not match the binary pair [7664-41-7,7732-18-5] - for now this is an error

CoolProp 6.6.0 has no fitted binary interaction parameters for ammonia/water
(ammonia has 13 partners in the database; water is not among them). The cubic
fallbacks do run, but return bubble pressure nearly independent of
concentration - 13.2 / 12.7 / 12.9 bar at 30 / 50 / 70% NH3 at 40 C, where the
true values span roughly 2 to 10 bar. That is not a small error; it erases the
solution field the cycle depends on. REFPROP has a proper model but is not
installed.

LiBr-H2O - half available. VLE *is* supported and is good: ``PropsSI('P', 'T',
T, 'Q', 0, 'INCOMP::LiBr[x]')`` reproduces the Duehring chart to ~1.5% (35 C /
55% gives an equivalent water saturation temperature of 5.05 C; 90 C / 60%
gives 44.4 C - both textbook). Valid for x in [0, 0.75] and T in [273, 500] K.
Density, cp and viscosity are fine too.

But its **enthalpy is unusable for this application**: h = 0 at 20 C for every
concentration independently, so it carries no heat of solution. Mixing 60% and
pure water to make 50% at constant temperature returns a heat of dilution of
0.4 J/kg where reality is -30 to -50 kJ/kg. The absorber and generator energy
balances are *entirely* about that missing term. Its enthalpy is also on a
different datum from CoolProp's ``'Water'`` (an 84 kJ/kg offset), so the two
cannot be mixed in one control volume without correction.

So: use CoolProp for LiBr VLE, density, cp and viscosity; supply h(T, x) here.
Supply everything here for NH3-H2O.

The refrigerant loops are unaffected - pure ammonia and pure water are fully
supported by CoolProp, so only the solution loop needs this package.

Interface each module should provide, so the components can stay
mixture-agnostic:

    x_saturated(T_celsius, P)  -> equilibrium liquid mass fraction
    P_saturated(T_celsius, x)  -> equilibrium pressure, Pa
    h_liquid(T_celsius, x)     -> solution specific enthalpy, J/kg
    h_vapor(T_celsius, P, x)   -> vapor specific enthalpy, J/kg
    cp_liquid(T_celsius, x)    -> solution specific heat, J/kg-K

The standard sources are the Patek-Klomfar correlations - 1995 for NH3-H2O,
2006 for LiBr-H2O. They are closed-form algebraic fits, add no dependencies,
and are what essentially every published absorption model uses. Only
``x_saturated`` needs a root-find (the relations are monotonic and well
behaved, so ``scipy.optimize.brentq`` is sufficient; scipy is already
installed).
"""
