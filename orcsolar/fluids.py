"""Canonical working-fluid identifiers used across this project.

CoolProp accepts more than one alias for the same substance - e.g. both
``'HEPTANE'`` and ``'NHEPTANE'`` resolve to identical n-heptane properties
(confirmed: both give Tcrit = 540.13 K). The three original notebooks used
both spellings for what is the same fluid; this module fixes one canonical
name so the rest of the code doesn't have to remember which alias was used
where.
"""

# Canonical CoolProp name for n-heptane. ORCModel (1).ipynb and
# ORCModelReheat.ipynb both spelled this 'HEPTANE'; ORCModelefficiencyplot.ipynb
# spelled it 'NHEPTANE'. Both are valid CoolProp aliases for the same fluid.
HEPTANE = "HEPTANE"

# All "dry" working fluids (positive-slope saturated-vapor line), screened in
# ORCModel (1).ipynb's driver cell.
BASELINE_SCREENING_FLUIDS = [
    "MM",
    "ISOPENTANE",
    "HEPTANE",
    "TOLUENE",
    "NOCTANE",
    "CYCLOPENTANE",
]
