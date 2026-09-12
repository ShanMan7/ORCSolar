"""Solution heat exchanger (SHX) for the absorption chiller.

STUB - not implemented. Governing equations below.

Structurally this is the chiller's answer to the ORC's recuperator: hot weak
solution heading from the generator to the absorber preheats cold strong
solution heading the other way, so the generator has less work to do. It is
worth roughly 20-30% on COP and essentially every real machine has one.

It cannot reuse ``hxgr.py``, despite the obvious family resemblance. That
module assumes a single fluid at equal mass flow on both sides, which is true
of an ORC recuperator. Here the two sides carry *different mass flows* - f on
the cold (strong) side against f-1 on the hot (weak) side, since the
difference left as refrigerant vapor - and different concentrations.

    Q_shx = (f - 1) * (h_c - h_c_out) = f * (h_b_out - h_b)

    effectiveness = (T_c - T_c_out) / (T_c - T_b)

Define effectiveness on whichever side carries C_min and be explicit about
which - with unequal flows the two definitions are not interchangeable, and
getting it backwards silently overstates recovered heat. Given the flow
asymmetry the hot side is usually, but not always, the limiting one; compute
both capacity rates rather than assuming.

``components/heat_exchanger.py`` already implements the generic
effectiveness definition for two Streams and may be reusable directly once the
mixture property model can supply cp for the solution.
"""


def recover(hot_in, cold_in, effectiveness, mixture):
    """Preheat strong solution using returning weak solution.

    Returns ``(hot_out, cold_out, Q_shx)``. See module docstring.
    """
    raise NotImplementedError(
        "Solution heat exchanger not implemented - needs a mixture property "
        "model for h(T, x) and cp(T, x). See orcsolar.mixtures."
    )
