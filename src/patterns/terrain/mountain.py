from patterns.builder import PatternBuilder
from patterns.registry import PatternRegistry


PatternRegistry.register(
    PatternBuilder('mountain', '🏔️')
    .color('#ffffff')
    .adjacent_to('grass', affinity=0.55)
    .adjacent_to('mountain', affinity=0.3)
    .adjacent_to('water', affinity=0.15)
    .build()
)