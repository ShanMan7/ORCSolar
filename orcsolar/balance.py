"""Energy-balance checks.

Every component and every cycle has to close: what goes in comes out. The
cycle modules already print a residual for exactly this reason, and it is the
cheapest possible guard against the most common modeling bug - a sign error
that silently produces a plausible-looking efficiency.

Worth keeping in mind once the chiller and the plant loop exist: a system that
returns cooling to the source of its own waste heat is precisely the shape of
model that can accidentally violate the second law. A closing energy balance is
necessary but *not* sufficient to prove it doesn't - heat must also be rejected
to a genuine ambient sink, not recycled internally.
"""


def residual(inlets=(), outlets=(), heat_in=0.0, work_out=0.0):
    """Energy imbalance around a control volume, in W.

        residual = sum(H_in) + heat_in - sum(H_out) - work_out

    inlets/outlets: iterables of Stream (their ``H`` is the enthalpy flow, W)
    heat_in: heat added to the control volume, W
    work_out: work produced by the control volume, W

    Zero means the control volume closes. Sign tells you which way it leaks.
    """
    return (
        sum(s.H for s in inlets)
        + heat_in
        - sum(s.H for s in outlets)
        - work_out
    )


def check(inlets=(), outlets=(), heat_in=0.0, work_out=0.0, rtol=1e-6, label="control volume"):
    """Raise if the energy balance does not close to within ``rtol``.

    Tolerance is relative to the largest energy flow crossing the boundary, so
    it stays meaningful whether the control volume passes watts or megawatts.
    Returns the residual (W) when it passes, so it can also be logged.
    """
    r = residual(inlets, outlets, heat_in, work_out)

    scale = max(
        [abs(s.H) for s in list(inlets) + list(outlets)] + [abs(heat_in), abs(work_out), 1.0]
    )
    if abs(r) > rtol * scale:
        raise AssertionError(
            f"{label} does not close: residual {r:.6g} W "
            f"({abs(r) / scale:.3e} relative, tolerance {rtol:.0e})"
        )
    return r
