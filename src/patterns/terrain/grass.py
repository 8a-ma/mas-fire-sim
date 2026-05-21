from patterns.builder import PatternBuilder
from patterns.registry import PatternRegistry

# Al importar este módulo, grass queda registrado automáticamente.
# No hace falta instanciar nada ni llamar ninguna función desde fuera.
#
# Lectura de las reglas:
#   grass puede tener como vecino:
#     - grass    (affinity 0.7) → tiende a formar extensiones amplias
#     - mountain (affinity 0.3) → puede aparecer en los bordes de montañas
#
# Para añadir un nuevo vecino al crearlo como tipo, añadir .adjacent_to().
# Para hacer grass más o menos común globalmente, ajustar las affinities
# relativas respecto a los otros patrones que también listen a grass.

PatternRegistry.register(
    PatternBuilder('grass', '🌿')
    .color('#1A7824')
    .adjacent_to('grass', affinity=0.9)
    .adjacent_to('mountain', affinity=0.3)
    .adjacent_to('water', affinity=0.2)
    .build()
)