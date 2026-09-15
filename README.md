# ORCSolar

An Organic Rankine Cycle (ORC) model for solar-thermal power, built on
[CoolProp](http://www.coolprop.org/) real-fluid properties. Models a
subcritical ORC (boiler/solar field -> turbine -> condenser -> pump), with
an optional internal recuperator variant, and screens candidate
working fluids and component efficiencies for thermal performance.

Being extended toward a full system model: data center waste heat, a solar
field, thermal storage, an ORC and an absorption chiller, with the ORC and
chiller competing for the same stored heat. The ORC is working; the rest is
scaffolded with the governing equations written into the stubs. See
[ARCHITECTURE.md](ARCHITECTURE.md) for the layer contracts, the conventions a
new block must follow, and what is built versus stubbed.

## Running it

```
pip install -r requirements.txt
python main.py          # the ORC - state tables for both cycles
python run_chiller.py   # the absorption chiller - state table + T-s + Duehring plots
```

The chiller takes its four defining temperatures on the command line:

```
python run_chiller.py --t-evap 5 --t-cond 40 --t-abs 35 --t-gen 90
```

This walks both cycles and prints each one's state table (T, P, h, s at every
state point) followed by its work, heat and efficiency terms.

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

The idea is that a component takes a state in and hands the next state back:

```python
s1 = boiler.outlet_state(185, "HEPTANE")        # saturated vapor at 185 C
s2, w_turbine = turbine.expand(s1, s3.P, 0.85, "HEPTANE")
```

and a cycle module is just those calls strung together in flow order. Each
one exposes a single function:

- `solve_states(T1, T_cond, fluid, ...)` - walks the cycle once and returns a
  dict of `{"states": {...}, "w_turbine", "w_pump", "w_net", "q_in",
  "q_out", "eta"}`. The recuperated cycle adds `"q_recuperated"`.

`main.py` calls it for both cycles and prints the results. Change `FLUID`,
`T_TURBINE_IN` or `T_CONDENSER` at the top of `main.py` to run a different
case.

Three modules are **not currently wired into `main.py`** - `plotting.py`,
`ts_diagram.py` (saturation domes for T-s diagrams) and
`calibration_data.py` (digitized literature data for validating the
recuperated cycle). They still work and are kept for when those outputs are
wanted again.

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
