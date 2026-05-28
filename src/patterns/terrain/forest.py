from patterns.builder import PatternBuilder
from patterns.registry import PatternRegistry


PatternRegistry.register(
    PatternBuilder('forest', '🌲')
    .adjacent_to('water', affinity=0.4)
    .adjacent_to('grass', affinity=0.2)
    .adjacent_to('mountain', affinity=0.1)
    .flammable(True)
    .color("#0e5906")
    .build()
)