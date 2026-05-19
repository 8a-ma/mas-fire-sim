from settings.settings import Settings
from environment.pattern import Pattern
from utils.wfc import WaveFunctionCollapse


def main():
    settings = Settings()

    print(f"🎮 Generador de Terreno - Wave Function Collapse")
    print(f"📏 Tamaño de grilla: {settings.GRID_SIZE}x{settings.GRID_SIZE}")
    print(f"🎨 Patrones disponibles: {len(Pattern.VALID_PATTERN)}")
    print()

    print("Patrones:")
    for pattern in Pattern.VALID_PATTERN:
        print(f"  {pattern['icon']} {pattern['type']}: {pattern['rules']}")
    print()

    wfc = WaveFunctionCollapse(
        patterns=Pattern.VALID_PATTERN,
        grid_size=settings.GRID_SIZE,
        seed=None  # Cambiar a un número específico para resultados reproducibles
    )

    print("🌍 Generando terreno...")
    success = wfc.generate()

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