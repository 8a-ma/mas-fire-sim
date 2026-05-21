from typing import Dict, List, Set


class PatternRegistry:
    """
    Registro central de todos los tipos de terreno.
 
    Los patrones se registran desde sus propios módulos (p.ej. grass.py)
    llamando a PatternRegistry.register(builder.build()).
    PatternRegistry nunca necesita importar ni conocer esos módulos.
    """

    _registry: Dict[str, Dict] = {}

    @classmethod
    def register(cls, pattern: Dict) -> None:
        """
        Registra un patrón construido con PatternBuilder
        """

        pattern_type = pattern['type']

        if pattern_type in cls._registry:
            raise ValueError(f"PatternRegistry: el tipo '{pattern_type}' ya está registrado")

        cls._registry[pattern_type] = pattern
    
    @classmethod
    def get_all_types(cls) -> Set[str]:
        """Retorna el conjunto de todos los tipos registrados."""
        
        return set(cls._registry.keys())
 
    @classmethod
    def get_icon_by_type(cls, pattern_type: str) -> str:
        """Retorna el emoji del tipo dado."""
        
        return cls._get(pattern_type)["icon"]
 
    @classmethod
    def get_neighbor_weights(cls, pattern_type: str) -> Dict[str, float]:
        """
        Retorna {tipo_vecino: affinity} para el tipo dado.
        Usado por wfc._get_weighted_type() al colapsar una celda.
        """
        
        rules = cls._get(pattern_type)["rules"]
        
        return {rule[0]: rule[1] for rule in rules}
 
    @classmethod
    def build_adjacency_map(cls) -> Dict[str, Set[str]]:
        """
        Retorna {tipo: {tipos_vecinos_permitidos}}.
        Usado por wfc._propagate() para filtrar posibilidades.
        """
        
        return {
            pattern_type: {rule[0] for rule in pattern["rules"]}
            for pattern_type, pattern in cls._registry.items()
        }

    @classmethod
    def _get(cls, pattern_type: str) -> Dict:
        """Obtiene un patrón por tipo o lanza error descriptivo."""
       
        if pattern_type not in cls._registry:
            
            registered = list(cls._registry.keys())
            
            raise ValueError(
                f"PatternRegistry: tipo '{pattern_type}' no encontrado. "
                f"Registrados: {registered}"
            )
        
        return cls._registry[pattern_type]