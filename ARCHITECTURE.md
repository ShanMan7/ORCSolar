# Architecture

How the pieces fit, and what a new block has to do to slot in. The point of
this file is that filling in a stub should be transcription, not design.

## Three layers

| Layer | Holds | Units | Time |
|---|---|---|---|
| `components/` | one device | `State` in, `State` out | none |
| `cycles/` | a closed loop of components | per-unit-mass, J/kg | none |
| `plant/` | the whole system network | `Stream`, kg/s and W | lives here |

**Components** are pure functions. Give one a state, it hands back the next
one. No memory, no globals, no time.

**Cycles** call components in flow order and report per-unit-mass terms, so a
cycle's answer is independent of plant size. That's what lets one ORC model
serve both temperature regimes at any capacity.

**Plant** is where kg/s, watts and (eventually) time appear. The bridge from
cycles to plant is mass flow: a cycle reports `q_in` in J/kg, the plant divides
available heat in W by it to get the kg/s the cycle can support, then scales
the rest of the per-kg terms by that.

The one block that breaks the pattern is **TES**, because it has memory — a
turbine's outlet depends only on its inlet, a tank's depends on its history.
That's why time belongs to `plant/` and nowhere else.

## State vs Stream

`State` is intensive — T, P, h, s. `Stream` is `State` + `mdot` + `fluid`.

Use `State` inside components and cycles. Use `Stream` at plant level, where
you split flows, mix returns, and carry several different fluids (water loops,
ORC working fluid, chiller solution) that must not get confused with each
other. `Stream.H` is enthalpy *flow* in W — that's the quantity that balances
at a junction.

## Conventions

Match these and everything downstream works:

- **One physical part per file**, named for the part. Function named for the
  action (`expand`, `compress`, `recuperate`, `absorb`, `desorb`) or
  `outlet_state` / `outlet_stream` for a terminal state.
- **`State.T` is always Kelvin.** Celsius appears only at function boundaries
  (parameters suffixed `_celsius`) and in printed output. Convert with
  `TK()` / `TC()` from `units.py`.
- **`fluid` is the last positional parameter** for State-based components; for
  Stream-based ones it rides on the Stream.
- **Work-producing or -consuming components return `(State, work)`.** Heat-only
  components return `State`, or a tuple of them. Sign convention: turbine
  `work = h_in - h_out` (positive producing), pump `work = h_out - h_in`
  (positive consuming).
- **Cycles return a dict**: `{"states": {"1": ..., }, "w_*", "q_*", "eta"}` —
  string keys, matching the state numbering in the module docstring. The
  chiller uses `cop` in place of `eta`.
- **Docstring names the equation** the code implements, and flags any preserved
  oddity as intentional (see the `+ 273.15` note in `components/hxgr.py`, which
  looks like a unit bug and is not).

## Filling in a stub

Every stub raises `NotImplementedError` and states in its docstring exactly
what equation is missing. The recipe:

1. Read the docstring — the governing equations are already written out.
2. If it needs mixture properties, check `mixtures/__init__.py` first. It
   records which properties CoolProp can and cannot supply, with evidence.
   Short version: NH3–H2O nothing, LiBr–H2O everything except enthalpy.
3. Implement, matching the conventions above.
4. Add a case to `tests/test_cycles.py`. If the block is part of a loop, assert
   the energy balance closes — `balance.check()` does this for Streams.

## Checking your work

`balance.py` computes `sum(H_in) + Q_in - sum(H_out) - W_out` around any
control volume. Both ORC cycles print this residual and it comes out exactly
zero; the tests assert it.

A closing energy balance is necessary but **not sufficient** here. This system
returns cooling to the source of its own waste heat, which is exactly the shape
that can manufacture free cooling. Heat has to leave through
`components/heat_rejection.py` to a real ambient sink — otherwise the model
will balance perfectly while breaking the second law.

Sanity anchors worth keeping in mind:

- ORC at 185 °C source / 35 °C sink: Carnot is 32.8%, this model gives 18.9%
  (baseline) and 22.1% (recuperated) — 58–67% of Carnot.
- ORC at 90 °C source: Carnot is 15.2%, so expect 6–9% real. If a low-temp
  result comes back at 15%, it's a bug.
- Single-effect chiller, T_gen 90 / T_amb 35 / T_evap 5 °C: reversible COP is
  1.40, real machines ~0.7. Far outside that band means a bug.

## Status

Working — under test (20 tests across `tests/`):

```
components/  boiler, turbine, condenser, pump, hxgr
             junction (split/mix), heat_exchanger, throttle
             absorber, generator, solution_pump
cycles/      baseline, recuperated, absorption (single-effect, no SHX)
mixtures/    lithium_bromide
state, units, fluids, balance
```

Run them: `python main.py` (ORC), `python run_chiller.py` (chiller + diagrams).

Stubbed — signature and equations documented, body raises:

```
components/  solar_collector, tes, data_center, heat_rejection
             solution_hx  (worth 20-30% on chiller COP)
mixtures/    ammonia_water (CoolProp supplies nothing; needs Patek-Klomfar 1995)
plant/       system (steady-state design point)
```

Validation anchors already established, useful as regression targets:

| Case | Result |
|---|---|
| ORC baseline / recuperated, heptane at 185 °C | 18.9% / 22.1% (matches notebooks) |
| Chiller at 5/44.4/35/90 °C | x 0.550→0.600, f = 12.08 (matches textbook) |
| Chiller at 5/40/35/90 °C | COP 0.644, 45.8% of reversible |
| Minimum generator temperature, 40/35 °C reject | 74.5 °C |
| All cycles | energy balance closes to ~1e-16 relative |

Present but not wired into `main.py`: `plotting.py`, `ts_diagram.py`,
`calibration_data.py`.
