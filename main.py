"""Master script for the ORCSolar model.

Runs, in order, everything the three original notebooks did - each stage
below is a direct port of one notebook's driver cell, now calling into the
shared ``orcsolar`` package instead of re-defining its own copy of the
physics:

  1. Baseline 4-state ORC   - screens 6 candidate working fluids for thermal
                               efficiency.                 (ORCModel (1).ipynb)
  2. Recuperated 6-state ORC - turbine/pump isentropic-efficiency sensitivity
                               study across the same fluid set.  (ORCModelReheat.ipynb)
  3. Model validation        - compares the recuperated-cycle model for
                               n-heptane against digitized literature data.
                                                   (ORCModelefficiencyplot.ipynb)

Every numeric result is printed to the console; every plot is saved as a PNG
under figures/ (created if needed) instead of only existing as an inline
notebook cell output.

Usage: python main.py
"""

from orcsolar import calibration_data, plotting
from orcsolar.cycles import baseline, recuperated
from orcsolar.fluids import BASELINE_SCREENING_FLUIDS
from orcsolar.units import TC


def section(title):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))


def run_baseline_screening(T1=185, T3=35, fluids=BASELINE_SCREENING_FLUIDS):
    """Port of ORCModel (1).ipynb's driver cell."""
    section("1. Baseline ORC - fluid screening")
    print(f"Turbine inlet T1={T1} C, condenser outlet T3={T3} C\n")

    sweep_curves = {}
    dome_curves = {}
    results = {}
    for fluid in fluids:
        inlet_T, eff = baseline.efficiency_sweep(fluid)
        sweep_curves[fluid] = (inlet_T, eff)

        result = baseline.run_cycle(T1, T3, fluid, verbose=False)
        results[fluid] = result
        dome_curves[fluid] = (result["dome_s"], result["dome_T"])

        print(
            f"  {fluid:<12s} eta = {result['eta']:5.1f} %   "
            f"turbine work = {result['wdot_t']/1000:7.1f} kJ/kg   "
            f"pump work = {result['wdot_p']/1000:6.2f} kJ/kg"
        )

    plotting.plot_efficiency_curves(
        sweep_curves,
        xlabel="Inlet Temperatures (K)",
        title="Inlet Temp vs Efficiency for Selected Fluids",
        filename="baseline_efficiency_vs_inlet_temp.png",
    )

    plotting.plot_ts_diagram(
        dome_curves,
        title="T-s diagram for Selected Fluids",
        filename="baseline_ts_diagram_combined.png",
    )

    for fluid, result in results.items():
        s_vals = [result["states"][k].s for k in "1234"]
        T_vals = [result["states"][k].T for k in "1234"]
        plotting.plot_ts_diagram(
            {fluid: dome_curves[fluid]},
            overlay_points={"cycle states": (s_vals, T_vals)},
            title=f"T-s diagram for {fluid}",
            filename=f"baseline_ts_diagram_{fluid}.png",
        )

    return results


def run_recuperated_sensitivity(T1=185, T4=35, fluids=BASELINE_SCREENING_FLUIDS):
    """Port of ORCModelReheat.ipynb's driver cell, extended to screen every
    fluid in BASELINE_SCREENING_FLUIDS.

    The original notebook's efficiency-vs-inlet-temp and T-s-diagram loops
    were already written as ``for F in Fluids`` - just only ever run with
    ``Fluids = ['HEPTANE']`` - so those generalize directly (one line/dome
    per fluid on shared, combined plots, same as section 1). Its turbine/pump
    sensitivity study instead called ``efficiencyPlot('HEPTANE', ...)`` with
    the fluid hardcoded as a literal string, not looped - so with 6 fluids
    that becomes one plot per fluid below (6 fluids x 3 values would be
    unreadable crammed onto a single combined plot).
    """
    section("2. Recuperated ORC - turbine/pump efficiency sensitivity")
    nt_values = [0.8, 0.85, 0.9]
    np_values = [0.65, 0.75, 0.8]

    # --- Efficiency vs. inlet temperature, all fluids, default efficiencies ---
    print(f"Turbine inlet T1={T1} C, condenser outlet T4={T4} C, default efficiencies\n")
    sweep_curves = {}
    dome_curves = {}
    for fluid in fluids:
        inlet_T, eff = recuperated.efficiency_sweep(fluid)
        sweep_curves[fluid] = (inlet_T, eff)

        result = recuperated.run_cycle(T1, T4, fluid, verbose=False)
        dome_curves[fluid] = (result["dome_s"], [TC(t) for t in result["dome_T"]])

        print(
            f"  {fluid:<12s} eta = {result['eta']:5.1f} %   "
            f"turbine work = {result['wdot_t']/1000:7.1f} kJ/kg   "
            f"pump work = {result['wdot_p']/1000:6.2f} kJ/kg"
        )

    plotting.plot_efficiency_curves(
        sweep_curves,
        xlabel="Inlet Temperatures (C)",
        title="Inlet Temp vs Efficiency for Selected Fluids",
        filename="recuperated_efficiency_vs_inlet_temp.png",
    )

    plotting.plot_ts_diagram(
        dome_curves,
        title="T-s diagram for Selected Fluids",
        filename="recuperated_ts_diagram_combined.png",
        temp_label="T (C)",
    )

    # --- Turbine / pump efficiency sensitivity, one plot per fluid ---
    print(f"\nTurbine/pump efficiency sensitivity at T1={T1} C, T4={T4} C:")
    for fluid in fluids:
        print(f"  {fluid}:")

        # Turbine sensitivity: sweep curves for the plot, plus single-point
        # (T1, T4) states to overlay on that fluid's T-s diagram - reuses
        # the dome already computed above instead of recomputing it 3x.
        nt_curves = {}
        overlay_points = {}
        for nt in nt_values:
            nt_curves[f"nt={nt}"] = recuperated.efficiency_sweep(fluid, eta_turbine=nt)
            point = recuperated.run_cycle(T1, T4, fluid, eta_turbine=nt, include_dome=False)
            print(f"    nt={nt:.2f}  eta = {point['eta']:5.1f} %")
            s_vals = [point["states"][k].s for k in "123456"]
            T_vals_C = [TC(point["states"][k].T) for k in "123456"]
            overlay_points[f"nt={nt}"] = (s_vals, T_vals_C)

        plotting.plot_efficiency_curves(
            nt_curves,
            xlabel="Inlet Temperatures (C)",
            title=f"Inlet Temp vs Efficiency for Different Turbine Efficiencies, {fluid}",
            filename=f"recuperated_efficiency_vs_nt_{fluid}.png",
        )

        plotting.plot_ts_diagram(
            {fluid: dome_curves[fluid]},
            overlay_points=overlay_points,
            title=f"T-s diagram for {fluid}",
            filename=f"recuperated_ts_diagram_{fluid}.png",
            temp_label="T (C)",
        )

        # Pump sensitivity: sweep curves for the plot only - the original
        # never overlaid pump-efficiency state points on a T-s diagram.
        np_curves = {}
        for npv in np_values:
            np_curves[f"np={npv}"] = recuperated.efficiency_sweep(fluid, eta_pump=npv)
            eta = recuperated.solve_states(T1, T4, fluid, eta_pump=npv)["eta"]
            print(f"    np={npv:.2f}  eta = {eta:5.1f} %")

        plotting.plot_efficiency_curves(
            np_curves,
            xlabel="Inlet Temperatures (C)",
            title=f"Inlet Temp vs Efficiency for Different Pump Efficiencies, {fluid}",
            filename=f"recuperated_efficiency_vs_np_{fluid}.png",
        )


def run_validation(fluid="NHEPTANE", T1_start=175):
    """Port of ORCModelefficiencyplot.ipynb - validates the recuperated-cycle
    model against digitized literature data ("Kashif's paper")."""
    section("3. Model validation vs. literature")

    inlet_T, eff = recuperated.efficiency_sweep(fluid, T1_start=T1_start)
    cal_x = calibration_data.NHEPTANE_INLET_TEMP_C
    cal_y = calibration_data.NHEPTANE_EFFICIENCY_PCT

    plotting.plot_calibration_overlay(
        (inlet_T, eff), (cal_x, cal_y), fluid=fluid,
        filename="validation_calibration_overlay.png",
    )

    # Numeric fit check (nearest-point comparison) - not in the original
    # notebook, which only compared the two curves visually; added here so
    # the master script can report a number, not just save a picture.
    errs = []
    for cx, cy in zip(cal_x, cal_y):
        idx = min(range(len(inlet_T)), key=lambda i: abs(inlet_T[i] - cx))
        errs.append(eff[idx] - cy)
    mae = sum(abs(e) for e in errs) / len(errs)
    print(f"{fluid}: model vs. digitized literature curve, mean absolute error = {mae:.3f} percentage points")


if __name__ == "__main__":
    run_baseline_screening()
    run_recuperated_sensitivity()
    run_validation()
    print("\nAll figures saved under ./figures/")
