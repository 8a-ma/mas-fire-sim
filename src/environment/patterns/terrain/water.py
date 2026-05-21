from environment.patterns.builder import PatternBuilder
from environment.patterns.registry import PatternRegistry


PatternRegistry.register(
    PatternBuilder('water', '💧')
    .color('#2FD6D4')
    .adjacent_to('water', affinity=0.2)
    .adjacent_to('grass', affinity=0.66)
    .adjacent_to('mountain', affinity=0.25)
    .build()
)
