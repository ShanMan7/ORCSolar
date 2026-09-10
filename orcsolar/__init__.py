"""orcsolar: an Organic Rankine Cycle (ORC) model for solar-thermal power.

This package is a component-by-component port of three research notebooks
(ORCModel (1).ipynb, ORCModelReheat.ipynb, ORCModelefficiencyplot.ipynb) into
plain, importable Python modules:

- ``orcsolar.components`` - one file per physical cycle component (boiler,
  turbine, condenser, pump, HXGR/recuperator). Each exposes small functions
  that take a thermodynamic :class:`~orcsolar.state.State` in and return one
  (or two, for the recuperator) out.
- ``orcsolar.cycles`` - assembles those components into full cycles:
  ``baseline`` (4-state, no heat recovery) and ``recuperated`` (6-state, with
  an internal HXGR).
- ``orcsolar.ts_diagram``, ``orcsolar.plotting``, ``orcsolar.calibration_data``,
  ``orcsolar.costing`` - supporting utilities used by ``main.py``.

See the top-level ``main.py`` for a runnable driver that reproduces every plot
and result the three original notebooks produced.
"""
