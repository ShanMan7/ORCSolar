"""Regression tests locking in the behavior that is known good.

These exist so that adding the chiller, the collector or the plant layer
cannot silently change the ORC results. The efficiency values below are not
invented - they are what the original notebooks produced and what the ported
package reproduces.

Run with:  python -m pytest tests/ -q
       or: python tests/test_cycles.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orcsolar.components import junction, throttle  # noqa: E402
from orcsolar.cycles import baseline, recuperated  # noqa: E402
from orcsolar.state import water_stream  # noqa: E402

# From the original notebooks' own cached output, at T1=185 C / T_cond=35 C.
NOTEBOOK_BASELINE_ETA = {
    "MM": 16.3,
    "ISOPENTANE": 18.3,
    "HEPTANE": 18.9,
    "TOLUENE": 21.8,
    "NOCTANE": 18.9,
    "CYCLOPENTANE": 21.1,
}


def test_baseline_matches_notebooks():
    for fluid, expected in NOTEBOOK_BASELINE_ETA.items():
        eta = baseline.solve_states(185, 35, fluid)["eta"]
        assert abs(eta - expected) < 0.05, f"{fluid}: {eta:.2f} != {expected}"


def test_recuperated_matches_notebooks():
    # Original notebook printed 21.0 / 22.1 / 23.1 % for nt = 0.80 / 0.85 / 0.90.
    for eta_turbine, expected in [(0.80, 21.0), (0.85, 22.1), (0.90, 23.1)]:
        eta = recuperated.solve_states(185, 35, "HEPTANE", eta_turbine=eta_turbine)["eta"]
        assert abs(eta - expected) < 0.05, f"nt={eta_turbine}: {eta:.2f} != {expected}"


def test_recuperator_beats_baseline():
    """The recuperator must reduce heat input without changing the work terms."""
    base = baseline.solve_states(185, 35, "HEPTANE")
    rec = recuperated.solve_states(185, 35, "HEPTANE")

    assert abs(rec["w_net"] - base["w_net"]) < 1.0  # same turbine and pump duty
    assert rec["q_in"] < base["q_in"]  # boiler does less work
    assert rec["eta"] > base["eta"]


def test_cycles_close_energy_balance():
    """q_in + w_pump == q_out + w_turbine, for both cycles."""
    for result in [
        baseline.solve_states(185, 35, "HEPTANE"),
        recuperated.solve_states(185, 35, "HEPTANE"),
    ]:
        residual = (result["q_in"] + result["w_pump"]) - (result["q_out"] + result["w_turbine"])
        assert abs(residual) < 1e-6 * result["q_in"], f"residual {residual:.6g} J/kg"


def test_split_conserves_mass_and_state():
    inlet = water_stream(60.0, mdot=2.0)
    a, b = junction.split(inlet, [0.25, 0.75])

    assert abs(a.mdot + b.mdot - inlet.mdot) < 1e-12
    assert a.T == inlet.T and b.T == inlet.T  # splitting changes flow, not state


def test_mix_conserves_energy():
    hot = water_stream(80.0, mdot=1.0)
    cold = water_stream(20.0, mdot=3.0)
    mixed = junction.mix([hot, cold])

    assert abs(mixed.mdot - 4.0) < 1e-12
    assert abs(mixed.H - (hot.H + cold.H)) < 1e-6
    assert cold.T < mixed.T < hot.T


def test_throttle_is_isenthalpic():
    inlet = water_stream(80.0, mdot=1.0, P=500000.0)
    outlet = throttle.expand_stream(inlet, P_out=200000.0)

    assert abs(outlet.h - inlet.h) < 1e-6
    assert outlet.P < inlet.P
    assert outlet.s > inlet.s  # throttling is irreversible


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ok  {name}")
            passed += 1
    print(f"\n{passed} passed")
