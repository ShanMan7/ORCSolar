"""Working fluids, grouped by the temperature regime they suit.

CoolProp accepts more than one alias for the same substance - e.g. both
``'HEPTANE'`` and ``'NHEPTANE'`` resolve to identical n-heptane properties
(confirmed: both give Tcrit = 540.13 K). The original notebooks used both
spellings for the same fluid; this module fixes one canonical name.

The two regimes exist because collector technology and working fluid have to
be chosen together - a fluid whose critical temperature sits below the source
temperature cannot run a subcritical cycle at all, and a fluid that needs
185 C is useless behind a flat-plate collector that cannot exceed ~100 C.
"""

# Canonical CoolProp name for n-heptane. ORCModel (1).ipynb and
# ORCModelReheat.ipynb spelled this 'HEPTANE'; ORCModelefficiencyplot.ipynb
# spelled it 'NHEPTANE'. Both are valid CoolProp aliases for the same fluid.
HEPTANE = "HEPTANE"

# High-temperature regime, ~150-185 C: concentrating collectors (parabolic
# trough). These are the six "dry" fluids (positive-slope saturated-vapor
# line) screened in the original notebooks.
HIGH_TEMP_FLUIDS = [
    "MM",
    "ISOPENTANE",
    "HEPTANE",
    "TOLUENE",
    "NOCTANE",
    "CYCLOPENTANE",
]

# Low-temperature regime, ~85-95 C: evacuated-tube or flat-plate collectors.
# CANDIDATES - not yet screened or validated in this model. The high-temp
# fluids above are mostly unusable down here (toluene and n-octane barely
# evaporate at 90 C), so this set needs its own screening run before any of it
# is trusted. R245fa is being phased down for GWP reasons; R1233zd(E) and
# R1336mzz(Z) are the common low-GWP replacements.
LOW_TEMP_CANDIDATES = [
    "R245fa",
    "R1233zd(E)",
    "ISOPENTANE",
    "ISOBUTANE",
    "R1234ze(Z)",
]

# Kept under its original name so existing callers keep working.
BASELINE_SCREENING_FLUIDS = HIGH_TEMP_FLUIDS

REGIMES = {
    "high_temp": HIGH_TEMP_FLUIDS,
    "low_temp": LOW_TEMP_CANDIDATES,
}
