"""Run the ORC models and print their state points.

Each cycle in orcsolar/cycles is just an assembly of the component models in
orcsolar/components - feed a component a state, it hands back the next one.
This script walks both cycles and prints the resulting state table plus the
work and heat terms.

Usage: python main.py
"""

from orcsolar.cycles import baseline, recuperated
from orcsolar.units import TC

FLUID = "HEPTANE"
T_TURBINE_IN = 185  # boiler outlet / turbine inlet, deg C
T_CONDENSER = 35  # condenser outlet / pump inlet, deg C

BASELINE_LABELS = {
    "1": "boiler out / turbine in",
    "2": "turbine out",
    "3": "condenser out / pump in",
    "4": "pump out / boiler in",
}

RECUPERATED_LABELS = {
    "1": "boiler out / turbine in",
    "2": "turbine out / HXGR hot in",
    "3": "HXGR hot out / cond in",
    "4": "condenser out / pump in",
    "5": "pump out / HXGR cold in",
    "6": "HXGR cold out / boiler in",
}


def print_states(result, labels):
    """Print one row per state point: where it is, and its T, P, h, s."""
    print(f"  {'':2} {'state':<28}{'T (C)':>9}{'P (kPa)':>11}{'h (kJ/kg)':>12}{'s (kJ/kg-K)':>13}")
    for key, state in result["states"].items():
        print(
            f"  {key:2} {labels[key]:<28}"
            f"{TC(state.T):>9.1f}{state.P / 1000:>11.1f}"
            f"{state.h / 1000:>12.1f}{state.s / 1000:>13.3f}"
        )


def print_energy(result):
    """Print the per-unit-mass work/heat terms and the efficiency."""
    print(f"  turbine work      {result['w_turbine'] / 1000:8.1f} kJ/kg")
    print(f"  pump work         {result['w_pump'] / 1000:8.1f} kJ/kg")
    print(f"  net work          {result['w_net'] / 1000:8.1f} kJ/kg")
    print(f"  heat in           {result['q_in'] / 1000:8.1f} kJ/kg")
    print(f"  heat rejected     {result['q_out'] / 1000:8.1f} kJ/kg")
    if "q_recuperated" in result:
        print(f"  heat recuperated  {result['q_recuperated'] / 1000:8.1f} kJ/kg")
    print(f"  efficiency        {result['eta']:8.1f} %")

    # Everything in has to come back out: q_in + w_pump == q_out + w_turbine.
    # A non-zero residual here means a component or a sign is wrong.
    residual = (result["q_in"] + result["w_pump"]) - (result["q_out"] + result["w_turbine"])
    print(f"  energy balance    {residual:8.1e} J/kg residual")


def main(fluid=FLUID, T1=T_TURBINE_IN, T_cond=T_CONDENSER):
    for title, result, labels in [
        ("BASELINE ORC", baseline.solve_states(T1, T_cond, fluid), BASELINE_LABELS),
        ("RECUPERATED ORC", recuperated.solve_states(T1, T_cond, fluid), RECUPERATED_LABELS),
    ]:
        print(f"\n{title} - {fluid}, turbine inlet {T1} C, condenser {T_cond} C")
        print("-" * 75)
        print_states(result, labels)
        print()
        print_energy(result)


if __name__ == "__main__":
    main()
