"""Steady-state design point for the whole system.

STUB - not implemented. The wiring is described here so that filling it in is
assembly rather than design.

Topology, from the system diagram:

    data center --(waste heat, T_dw)--> flow control ----> solar field --(T_s)--+
                                              |                                 |
                                              +---------------------------------+--> TES (T_t)
                                                                                     |
                                       +---------------------------------------------+
                                       |                                             |
                                  ORC (power, rejects at T_o)          absorption chiller (T_dh)
                                       |                                             |
                                       +--> heat rejection <-------------------------+
                                                                                     |
                                                            chilled water (T_a2) --> data center

Two things about this topology drive everything:

1. **The ORC and the chiller compete for the same heat.** Both draw from the
   TES at T_t. Splitting that flow between power and cooling is the central
   control decision - it is what the "AI-Enabled Smart Control" box in the
   diagram decides, and the question the rest of the model exists to answer.
   Expose the split as an explicit parameter so it can be swept.

2. **The cooling loop closes on itself.** Chilled water cools the data center,
   whose waste heat partly drives the chiller that produced it. This is exactly
   the shape of model that can accidentally manufacture free cooling. Heat must
   leave through ``heat_rejection`` to a real ambient sink, and
   ``orcsolar.balance.check`` should be called on the whole plant boundary, not
   just on individual blocks.

Steady-state means TES is a fixed-temperature node here: charge equals
discharge, and its only loss is standing loss. The transient version - where
T_t moves and storage genuinely buffers - belongs in a separate driver that
calls this one per timestep.

Both temperature regimes are meant to run through this same function, since
what changes between them is component parameters and fluid choice, not
topology:

    low temperature   ~85-95 C    evacuated tube / flat plate, single-effect
                                  chiller, low-temp ORC fluid
    high temperature  ~150-185 C  parabolic trough, double-effect chiller
                                  possible, current ORC fluids

See ``orcsolar.fluids`` for the fluid sets keyed by regime.
"""


def solve_design_point(
    P_IT,
    irradiance,
    T_ambient_celsius,
    T_storage_celsius,
    heat_split_to_orc,
    orc_fluid,
    mixture,
):
    """Solve the whole plant at one steady operating point.

    heat_split_to_orc: fraction of TES output sent to the ORC; the remainder
        drives the chiller. The parameter to sweep.

    Intended to return a dict of the plant-level results - net power, cooling
    delivered, heat rejected, ORC efficiency, chiller COP, and the overall
    energy-balance residual - plus the sub-results from each cycle.
    """
    raise NotImplementedError(
        "Plant design point not implemented. Needs: solar_collector, tes, "
        "data_center, heat_rejection and the absorption cycle. The ORC side "
        "(cycles.baseline / cycles.recuperated) is ready to wire in."
    )
