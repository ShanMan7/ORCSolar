"""Digitized reference data used to validate the recuperated-cycle model
against published literature.

Ported verbatim from ORCModelefficiencyplot.ipynb, which overlaid these
19 hand-digitized (inlet-temperature, efficiency) points - almost certainly
lifted from a figure in "Kashif's paper" (referenced throughout the original
notebooks for isentropic-efficiency assumptions and cost correlations, but
never fully cited anywhere in the repo) - against the model's own computed
curve for n-heptane.
"""

NHEPTANE_INLET_TEMP_C = [
    181, 186, 191, 196, 201, 206, 211, 216, 221, 226,
    231, 236, 241, 246, 251, 256, 261, 263, 266,
]

NHEPTANE_EFFICIENCY_PCT = [
    22.15, 22.60, 22.97, 23.34, 23.73, 24.10, 24.47, 24.77, 25.08, 25.40,
    25.70, 25.92, 26.15, 26.40, 26.57, 26.77, 26.82, 26.85, 26.79,
]
