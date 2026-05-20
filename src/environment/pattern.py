from typing import List, Dict, Set


class Pattern:
    """
    Define los tipos de terreno disponibles y sus reglas de adyacencia.
    
    Estructura de cada patrón:
    {
        'type': str,           # Identificador único del patrón
        'icon': str,           # Emoji para renderizar
        'rules': [
            [tipo_adyacente, probabilidad],  # índice 0: tipo, índice 1: probabilidad
            ...
        ],
        'color': str           # Color hexadecimal
    }
    """
    
    VALID_PATTERN: List[Dict] = [
        {
            'type': 'grass',
            'icon': '🌿',
            'rules': [
                ['grass', 0.9],
                ['mountain', 0.1],
            ],
            'color': '#1A7824'
        },
        {
            'type': 'water',
            'icon': '💧',
            'rules': [
                ['water', 0.2],
                ['grass', 0.45],
                ['mountain', 0.25],
            ],
            'color': '#2FD6D4'
        },
        {
            'type': 'mountain',
            'icon': '🏔️',
            'rules': [
                ['grass', 0.55],
                ['mountain', 0.3],
                ['water', 0.15]
            ],
            'color': '#ffffff'
        }
    ]

    @classmethod
    def get_all_types(cls) -> Set[str]:
        """Retorna un conjunto con todos los tipos de terreno disponibles."""

        return {pattern['type'] for pattern in cls.VALID_PATTERN}

    @classmethod
    def get_pattern_by_type(cls, pattern_type: str) -> Dict:
        """Retorna el patrón correspondiente a un tipo específico."""

        for pattern in cls.VALID_PATTERN:
            if pattern['type'] == pattern_type: return pattern
        
        raise ValueError(f"Patrón no encontrado: {pattern_type}")

    @classmethod
    def get_icon_by_type(cls, pattern_type: str) -> str:
        """Retorna el emoji de un tipo específico."""

        pattern = cls.get_pattern_by_type(pattern_type)

        return pattern['icon']
    
    @classmethod
    def get_adjacent_types(cls, pattern_type: str) -> Set[str]:
        """
        Retorna los tipos que pueden ser adyacentes a un tipo dado.
        """

        pattern = cls.get_pattern_by_type(pattern_type)

        return {rule[0] for rule in pattern['rules']}

    @classmethod
    def get_neighbor_weights(cls, pattern_type: str) -> Dict[str, float]:
        """
        Retorna los pesos que este patrón le asigna a cada tipo vecino.
        """

        pattern = cls.get_pattern_by_type(pattern_type)

        return {rule[0]: rule[1] for rule in pattern['rules']}

    @classmethod
    def build_adjacency_map(cls) -> Dict[str, Set[str]]:
        """
        Construye un mapa de adyacencia entre todos los tipos.
        """

        adjacency = {}

        for pattern in cls.VALID_PATTERN:
            adjacency[pattern['type']] = cls.get_adjacent_types(pattern['type'])
        
        return adjacency