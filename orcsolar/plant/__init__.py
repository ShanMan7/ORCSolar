"""Plant layer - the whole system, above the level of a single cycle.

The three layers, and why they are separate:

    components/   one device. State in, state out. No memory, no time.
    cycles/       a closed loop of components. Per-unit-mass (J/kg), so the
                  answer is independent of plant size.
    plant/        the network: data center, solar field, TES, ORC, chiller and
                  heat rejection wired together, in Streams (kg/s and W).

The bridge between cycles and plant is mass flow. A cycle reports ``q_in`` in
J/kg; the plant divides the heat actually available in W by it to get the kg/s
of working fluid the cycle can support, then scales the rest of the cycle's
per-kg terms by that. Keeping cycles size-agnostic is what lets the same ORC
model serve both temperature regimes and any plant capacity.

Time lives here and nowhere else. Components and cycles stay steady-state; when
the model goes transient, this layer owns the loop, and TES is the reason - it
is the only block with memory (see ``components/tes.py``).
"""
