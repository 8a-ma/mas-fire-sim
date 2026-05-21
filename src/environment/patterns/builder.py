from typing import Dict


class PatternBuilder:
    """
    Construye un patrón de terreno con una interfaz fluida.
    Valida que todos los campos obligatorios estén presentes antes de build().
 
    Uso:
        pattern = (
            PatternBuilder("grass", "🌿")
            .color("#1A7824")
            .adjacent_to("grass",    affinity=0.7)
            .adjacent_to("mountain", affinity=0.3)
            .build()
        )

    Campos:
        type     — identificador único del patrón
        icon     — emoji que se renderiza en terminal
        color    — color hexadecimal (uso futuro, p.ej. exportación HTML)
        rules    — lista de [tipo_vecino, affinity] donde affinity es la
                   probabilidad relativa de que ese tipo aparezca como vecino.
                   Los valores no necesitan sumar 1; se normalizan al colapsar.
    """

    def __init__(self, pattern_type: str, icon: str):
        self._type = pattern_type
        self._icon = icon
        self._color = '#000000'
        self._rules = []
    
    def color(self, hex_color: str) -> 'PatternBuilder':
        self._color = hex_color
        
        return self

    def adjacent_to(self, neighbor_type: str, affinity: float) -> 'PatternBuilder':
        """
        Declara que este patrón puede tener `neighbor_type` como vecino,
        con la afinidad dada.
 
        La afinidad es un peso relativo: no necesita sumar 1 entre todas
        las reglas. Cuanto mayor sea respecto a las demás, más probable
        será ese vecino al colapsar.
        """

        if affinity < 0:
            raise ValueError(f"La afinidad debe ser >= 0, se recibió {affinity}")
        
        self._rules.append([neighbor_type, affinity])

        return self

    def build(self) -> Dict:
        """
        Valida los campos y retorna el diccionario de patrón listo para
        ser registrado en PatternRegistry.
        """

        self._validate()

        return {
            'type': self._type,
            'icon': self._icon,
            'color': self._color,
            'rules': self._rules,
        }
    
    def _validate(self) -> None:
        if not self._type:
            raise ValueError("PatternBuilder: 'type' no puede estar vacío.")
        
        if not self._icon:
            raise ValueError(f"PatternBuilder '{self._type}': 'icon' no puede estar vacío.")

        if not self._rules:
            raise ValueError(f"PatternBuilder '{self._type}': debe tener al menos una regla. ")
