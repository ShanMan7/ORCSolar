"""Tests for the single-effect absorption chiller.

The important one is ``test_reproduces_textbook_operating_point``: the model is
given only four temperatures and independently arrives at the concentrations
and circulation ratio of the standard worked example. Nothing about x or f is
fed in.
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CoolProp.CoolProp import PropsSI  # noqa: E402

from orcsolar.cycles import absorption  # noqa: E402
from orcsolar.mixtures import lithium_bromide as libr  # noqa: E402

# Reference design point. Note the condenser is 44.4 C, not 40: the textbook
# example pairs a 90 C generator with x_weak = 0.60, and the Duehring relation
# fixes the matching condenser temperature at 44.4 C.
REF = dict(T_evaporator=5.0, T_condenser=44.4, T_absorber=35.0, T_generator=90.0)


def test_reproduces_textbook_operating_point():
    r = absorption.solve_states(mixture=libr, **REF)
    assert abs(r["x_strong"] - 0.55) < 0.01, r["x_strong"]
    assert abs(r["x_weak"] - 0.60) < 0.01, r["x_weak"]
    assert abs(r["f"] - 12.0) < 0.3, r["f"]


def test_energy_balance_closes():
    """q_evap + q_gen + w_pump == q_cond + q_abs, to machine precision."""
    for T_gen in (80.0, 90.0, 105.0):
        r = absorption.solve_states(5.0, 40.0, 35.0, T_gen, libr)
        residual = absorption.energy_balance_residual(r)
        assert abs(residual) < 1e-6 * r["q_gen"], f"T_gen={T_gen}: {residual:.6g} J/kg"


def test_evaporator_duty_matches_hand_calculation():
    """q_evap is just h_g(T_evap) - h_f(T_cond), the refrigerant doing its job."""
    r = absorption.solve_states(5.0, 40.0, 35.0, 90.0, libr)
    expected = PropsSI("H", "T", 278.15, "Q", 1, "Water") - PropsSI("H", "T", 313.15, "Q", 0, "Water")
    assert abs(r["q_evap"] - expected) < 1.0


def test_cop_below_reversible():
    """Second law: a real machine cannot beat the reversible bound."""
    for T_gen in (80.0, 90.0, 105.0, 120.0):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = absorption.solve_states(5.0, 40.0, 35.0, T_gen, libr)
        assert 0 < r["cop"] < r["cop_reversible"], (
            f"T_gen={T_gen}: COP {r['cop']:.4f} vs reversible {r['cop_reversible']:.4f}"
        )


def test_cop_in_expected_band_without_shx():
    """Single-effect LiBr with no solution heat exchanger lands near 0.6-0.7.

    Textbook values of 0.70-0.80 assume an SHX, which this cycle omits - it is
    worth 20-30%, which brings 0.64 into that range.
    """
    r = absorption.solve_states(5.0, 40.0, 35.0, 90.0, libr)
    assert 0.55 < r["cop"] < 0.72, r["cop"]


def test_cop_improves_with_hotter_generator():
    cops = []
    for T_gen in (80.0, 85.0, 90.0, 95.0, 100.0):
        cops.append(absorption.solve_states(5.0, 40.0, 35.0, T_gen, libr)["cop"])
    assert cops == sorted(cops), cops


def test_degassing_collapse_raises():
    """Too cold a generator must fail loudly, not return a plausible number."""
    try:
        absorption.solve_states(5.0, 40.0, 35.0, 65.0, libr)
    except ValueError as e:
        assert "degassing width" in str(e)
    else:
        raise AssertionError("expected a ValueError when the degassing width collapses")


def test_circulation_ratio_diverges_near_the_limit():
    """As the degassing width narrows, f must blow up - the failure mode."""
    wide = absorption.solve_states(5.0, 40.0, 35.0, 100.0, libr)
    narrow = absorption.solve_states(5.0, 40.0, 35.0, 76.0, libr)
    assert narrow["f"] > 5 * wide["f"], (narrow["f"], wide["f"])
    assert narrow["degassing_width"] < wide["degassing_width"]


def test_solution_valve_is_isenthalpic():
    r = absorption.solve_states(5.0, 40.0, 35.0, 90.0, libr)
    c, d = r["states"]["c"], r["states"]["d"]
    assert abs(c.h - d.h) < 1e-9
    assert abs(c.x - d.x) < 1e-12
    assert d.P < c.P


def test_refrigerant_throttle_is_isenthalpic():
    r = absorption.solve_states(5.0, 40.0, 35.0, 90.0, libr)
    s3, s4 = r["states"]["3"], r["states"]["4"]
    assert abs(s3.h - s4.h) < 1e-9
    assert s4.s > s3.s  # irreversible


def test_libr_enthalpy_carries_heat_of_solution():
    """The reason ASHRAE is used instead of CoolProp's LiBr enthalpy.

    Diluting concentrated solution must release heat. CoolProp returns ~0 here.
    """
    T = 20.0
    q = (
        1.0 * libr.h_liquid(T, 0.60)
        + 0.2 * PropsSI("H", "T", 273.15 + T, "Q", 0, "Water")
        - 1.2 * libr.h_liquid(T, 0.50)
    )
    assert 20e3 < q < 80e3, f"heat of dilution {q/1000:.1f} kJ is not physical"


def test_libr_dhdt_matches_coolprop_cp():
    """Independent check on the ASHRAE correlation's temperature dependence."""
    for T in (40.0, 60.0, 90.0):
        for x in (0.50, 0.60):
            dhdT = (libr.h_liquid(T + 0.01, x) - libr.h_liquid(T - 0.01, x)) / 0.02
            cp = libr.cp_liquid(T, x)
            assert abs(dhdT - cp) / cp < 0.05, f"T={T} x={x}: {dhdT:.1f} vs {cp:.1f}"


def test_x_saturated_inverts_p_saturated():
    for T, x in ((35.0, 0.55), (90.0, 0.60), (60.0, 0.50)):
        assert abs(libr.x_saturated(T, libr.P_saturated(T, x)) - x) < 1e-6


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ok  {name}")
            passed += 1
    print(f"\n{passed} passed")
