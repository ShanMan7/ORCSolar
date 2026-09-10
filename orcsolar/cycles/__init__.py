"""Full-cycle assemblies built from the individual components in
``orcsolar.components``.

- ``baseline``: boiler -> turbine -> condenser -> pump (4 states), ported
  from ORCModel (1).ipynb.
- ``recuperated``: boiler -> turbine -> HXGR(hot side) -> condenser -> pump
  -> HXGR(cold side) (6 states), ported from ORCModelReheat.ipynb.
"""
