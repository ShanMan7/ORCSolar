# ORCSolar

An Organic Rankine Cycle (ORC) model for solar-thermal power, built on
[CoolProp](http://www.coolprop.org/) real-fluid properties. Models a
subcritical ORC (boiler/solar field -> turbine -> condenser -> pump), with
an optional internal recuperator variant, and screens candidate
working fluids and component efficiencies for thermal performance.

## Running it

```
pip install -r requirements.txt
python main.py
```

This prints efficiency/work results for every case to the console and saves
every plot as a PNG under `figures/` (created automatically).

## Structure

The model logic used to live duplicated across three Jupyter notebooks
(`ORCModel (1).ipynb`, `ORCModelReheat.ipynb`, `ORCModelefficiencyplot.ipynb`
- still present in the repo for reference, but no longer where changes should
be made). It's now a plain importable package, `orcsolar/`, with one file per
physical cycle component and one file per full-cycle assembly:

```
orcsolar/
├── state.py              # shared State(T, P, h, s) point used everywhere
├── units.py               # TC() / TK() Celsius<->Kelvin helpers
├── fluids.py               # canonical fluid names / the 6-fluid screening list
├── ts_diagram.py           # saturation-dome (T-s backbone) calculation
├── calibration_data.py     # digitized literature data (n-heptane validation)
├── costing.py              # ported-but-unvalidated equipment cost correlations
├── plotting.py              # shared plot builders, save PNGs to figures/
├── components/
│   ├── boiler.py            # heat addition -> saturated vapor at T1
│   ├── turbine.py            # expansion, isentropic efficiency
│   ├── condenser.py           # heat rejection -> saturated liquid at T_cond
│   ├── pump.py                 # compression, isentropic efficiency
│   └── hxgr.py                  # internal recuperator (recuperated cycle only)
└── cycles/
    ├── baseline.py               # boiler -> turbine -> condenser -> pump (4 states)
    └── recuperated.py             # + hxgr, 6 states

main.py                              # master script: runs every stage below, in order
```

`main.py` runs, in order:

1. **Baseline screening** - 4-state cycle efficiency for 6 candidate fluids
   (MM, isopentane, heptane, toluene, n-octane, cyclopentane) at a fixed
   turbine-inlet/condenser temperature, plus T-s diagrams for each.
2. **Recuperated sensitivity study** - 6-state (recuperated) cycle for
   heptane, sweeping turbine and pump isentropic efficiency.
3. **Validation** - the recuperated-cycle model for n-heptane, compared
   against 19 digitized points from the literature reference the original
   notebooks call "Kashif's paper" (never fully cited in the repo).

Each cycle module exposes three functions with the same shape:

- `solve_states(...)` - the cheap core: solves every state point once, no
  plotting or printing. Used internally by the other two.
- `run_cycle(...)` - one detailed pass (optionally `verbose=True` to print
  the full state/work/efficiency breakdown), with the T-s saturation dome
  attached by default.
- `efficiency_sweep(...)` - sweeps turbine-inlet temperature from a start
  value up to the fluid's critical temperature, returning the
  temperature/efficiency arrays used for the efficiency-vs-temperature plots.

## Notes carried over from the original notebooks

- Turbine/pump isentropic efficiencies default to 0.85 / 0.65, and the HXGR
  effectiveness defaults to 0.9 - all three are cited only as "from Kashif's
  paper" / "an estimate given by previous research"
- `orcsolar/components/hxgr.py` preserves an original formula that looks at
  first glance like a duplicated unit conversion (Celsius added to an
  already-Kelvin value). It isn't a bug: dropping it moves the model's
  output away from the literature validation curve in step 3 above (verified
  numerically - see the comment in that file). Don't "fix" it without
  checking against the source paper first.
- `orcsolar/costing.py` ports the equipment cost correlations that were
  present but commented-out (and, in the recuperated notebook, explicitly
  self-flagged as "currently incorrect") in the original notebooks. They are
  not wired into `main.py` and should be treated as unvalidated.
