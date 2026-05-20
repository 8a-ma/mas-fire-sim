from collections import Counter
from settings.settings import Settings
from environment.pattern import Pattern
from utils.wfc import WaveFunctionCollapse


def get_terrain_stats(wfc):
    """Retorna estadísticas del terreno generado."""
    terrain = wfc.terrain
    types = []
    
    for r in range(terrain.grid_size):
        for c in range(terrain.grid_size):
            cell = terrain.get_cell(r, c)
            types.append(cell.get_pattern_type())
    
    total = len(types)
    counts = Counter(types)
    
    print(f"\n📊 Estadísticas del Terreno ({terrain.grid_size}x{terrain.grid_size}):")
    print(f"Total de celdas: {total}")
    for pattern_type, count in counts.most_common():
        percentage = (count / total) * 100
        print(f"  {pattern_type:12} {count:3} celdas ({percentage:5.1f}%)")


def main():
    settings = Settings()

    print(f"🎮 Generador de Terreno - Wave Function Collapse")
    print(f"📏 Tamaño de grilla: {settings.GRID_SIZE}x{settings.GRID_SIZE}")
    print(f"🎨 Patrones disponibles: {len(Pattern.VALID_PATTERN)}")
    print()

    print("Patrones:")
    for pattern in Pattern.VALID_PATTERN:
        # Extraer tipos y probabilidades de las reglas
        rules_str = ", ".join([f"{rule[0]}({rule[1]})" for rule in pattern['rules']])
        print(f"  {pattern['icon']} {pattern['type']}: {rules_str}")
    print()

    wfc = WaveFunctionCollapse(
        grid_size=settings.GRID_SIZE,
        seed=None  # Cambiar a un número específico para resultados reproducibles
    )

    print("🌍 Generando terreno...")
    success = wfc.generate(max_attempts=4)

    if not success:
        print("❌ Error: No se pudo generar un terreno válido después de varios intentos.")
        return

    print("✅ ¡Terreno generado exitosamente!")
    print()
    print("=" * (settings.GRID_SIZE * 2))
    print(wfc.render())
    print("=" * (settings.GRID_SIZE * 2))
    print()

if __name__ == '__main__':
    main()