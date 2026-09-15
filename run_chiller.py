"""Run the absorption chiller on its own and draw its diagrams.

Independent of main.py (the ORC) - this solves the chiller at one design
point, prints the state table, and saves a T-s diagram plus a Duehring plot.

    python run_chiller.py
    python run_chiller.py --t-evap 7 --t-cond 38 --t-abs 33 --t-gen 95
    python run_chiller.py --no-plots

Four temperatures define the machine:

    --t-evap   chilled-water side; the cooling you deliver
    --t-cond   refrigerant condensing; set by heat rejection to ambient
    --t-abs    absorber; also set by heat rejection, usually a few K below
               the condenser
    --t-gen    firing temperature; what the solar field or waste heat supplies

Only two of these are free in practice: the evaporator follows the cooling
duty, and the condenser and absorber both follow the ambient. The generator
temperature is the one you are really choosing, and there is a minimum below
which the degassing width collapses and no cycle exists at all - the script
reports it.
"""

import argparse
import warnings

from orcsolar.cycles import absorption
from orcsolar.mixtures import lithium_bromide
from orcsolar.units import TC

MIXTURES = {"libr": lithium_bromide}

REFRIGERANT_LABELS = {
    "1": "evaporator out / absorber in",
    "2": "generator out / condenser in",
    "3": "condenser out / throttle in",
    "4": "throttle out / evaporator in",
}

SOLUTION_LABELS = {
    "a": "absorber out / pump in",
    "b": "pump out / generator in",
    "c": "generator out / valve in",
    "d": "valve out / absorber in",
}


def print_report(result):
    inp = result["inputs"]
    print(f"\nABSORPTION CHILLER - {result['mixture']}")
    print(
        f"evaporator {inp['T_evaporator']} C | condenser {inp['T_condenser']} C | "
        f"absorber {inp['T_absorber']} C | generator {inp['T_generator']} C"
    )
    print("-" * 78)

    s = result["states"]

    print(f"  {'':2} {'refrigerant loop':<30}{'T (C)':>9}{'P (kPa)':>11}"
          f"{'h (kJ/kg)':>12}{'s (kJ/kg-K)':>13}")
    for k, label in REFRIGERANT_LABELS.items():
        st = s[k]
        print(f"  {k:2} {label:<30}{TC(st.T):>9.1f}{st.P/1000:>11.3f}"
              f"{st.h/1000:>12.1f}{st.s/1000:>13.3f}")

    print(f"\n  {'':2} {'solution loop':<30}{'T (C)':>9}{'P (kPa)':>11}"
          f"{'h (kJ/kg)':>12}{'x (LiBr)':>13}")
    for k, label in SOLUTION_LABELS.items():
        st = s[k]
        print(f"  {k:2} {label:<30}{TC(st.T):>9.1f}{st.P/1000:>11.3f}"
              f"{st.h/1000:>12.1f}{st.x:>13.4f}")

    print(f"\n  strong solution x   {result['x_strong']:8.4f}  (dilute in LiBr, leaves absorber)")
    print(f"  weak solution x     {result['x_weak']:8.4f}  (concentrated, leaves generator)")
    print(f"  degassing width     {result['degassing_width']:8.4f}")
    print(f"  circulation ratio f {result['f']:8.2f}  kg solution per kg refrigerant")

    print(f"\n  cooling  q_evap     {result['q_evap']/1000:8.1f} kJ/kg  <- the useful output")
    print(f"  heat in  q_gen      {result['q_gen']/1000:8.1f} kJ/kg  <- what you pay")
    print(f"  rejected q_cond     {result['q_cond']/1000:8.1f} kJ/kg")
    print(f"  rejected q_abs      {result['q_abs']/1000:8.1f} kJ/kg")
    print(f"  pump     w_pump     {result['w_pump']/1000:8.3f} kJ/kg")
    print(f"\n  COP                 {result['cop']:8.4f}")
    print(f"  COP reversible      {result['cop_reversible']:8.4f}"
          f"   ({result['cop']/result['cop_reversible']*100:.1f}% of it)")

    residual = absorption.energy_balance_residual(result)
    scale = abs(result["q_gen"])
    print(f"  energy balance      {residual:8.1e} J/kg residual "
          f"({abs(residual)/scale:.1e} relative)")


def minimum_generator_temperature(T_evap, T_cond, T_abs, mixture, T_max=200.0, step=2.0):
    """Coldest generator temperature that still opens a degassing width.

    Scans upward for the first feasible point, then refines. It deliberately
    does NOT bisect a fixed [lo, hi] bracket: the feasible window is bounded at
    **both** ends - too cold and the degassing width collapses, too hot and the
    concentration the generator would need runs past the property model's limit
    - so a bisection starting at a high `hi` can land on the upper bound, read
    it as "too cold", and walk away from the answer entirely.

    Returns None if no generator temperature works at these reject conditions.

    Warnings are suppressed because the scan probes well outside the operating
    point; those warnings describe the probes, not the machine being reported.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lo = None
        hi = None
        T = T_abs + step
        while T <= T_max:
            try:
                absorption.solve_states(T_evap, T_cond, T_abs, T, mixture)
                hi = T
                break
            except ValueError:
                lo = T
                T += step

        if hi is None:
            return None
        if lo is None:
            return hi

        for _ in range(40):
            mid = (lo + hi) / 2
            try:
                absorption.solve_states(T_evap, T_cond, T_abs, mid, mixture)
                hi = mid
            except ValueError:
                lo = mid
    return hi


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--t-evap", type=float, default=5.0, help="evaporator temperature, C")
    p.add_argument("--t-cond", type=float, default=40.0, help="condenser temperature, C")
    p.add_argument("--t-abs", type=float, default=35.0, help="absorber temperature, C")
    p.add_argument("--t-gen", type=float, default=90.0, help="generator temperature, C")
    p.add_argument("--eta-pump", type=float, default=absorption.DEFAULT_ETA_PUMP,
                   help="solution pump isentropic efficiency")
    p.add_argument("--mixture", choices=sorted(MIXTURES), default="libr")
    p.add_argument("--no-plots", action="store_true", help="skip figure generation")
    args = p.parse_args()

    mixture = MIXTURES[args.mixture]

    try:
        result = absorption.solve_states(
            args.t_evap, args.t_cond, args.t_abs, args.t_gen, mixture,
            eta_pump=args.eta_pump,
        )
    except ValueError as e:
        print(f"\nNo cycle exists at these conditions:\n  {e}")
        T_min = minimum_generator_temperature(args.t_evap, args.t_cond, args.t_abs, mixture)
        if T_min is not None:
            print(f"\nMinimum generator temperature for evaporator {args.t_evap} C, "
                  f"condenser {args.t_cond} C, absorber {args.t_abs} C: {T_min:.1f} C")
        raise SystemExit(1)

    print_report(result)

    T_min = minimum_generator_temperature(args.t_evap, args.t_cond, args.t_abs, mixture)
    if T_min is None:
        print("\n  minimum generator temperature: none found in range")
    else:
        print(f"\n  minimum generator temperature at these reject conditions: {T_min:.1f} C")
        print(f"  (you are firing at {args.t_gen:.1f} C, {args.t_gen - T_min:+.1f} K above it)")

    if not args.no_plots:
        from orcsolar import plotting

        ts = plotting.plot_chiller_ts(result, mixture)
        duehring = plotting.plot_chiller_duehring(result, mixture)
        print(f"\n  T-s diagram (refrigerant loop): {ts}")
        print(f"  Duehring plot (solution loop):  {duehring}")


if __name__ == "__main__":
    main()
