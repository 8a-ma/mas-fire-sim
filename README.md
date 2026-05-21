# Descripción
Simulación multi-agente de extinción de incendios forestales. Motor de consenso distribuido con drones, agentes terrestres y aéreos sobre un grid 256×256.

# Problema
Un incendio forestal se propaga en un grid 2D discreto. Tres tipos de agentes operan simultáneamente: observadores que detectan focos nuevos con visión parcial, terrestres que contienen el fuego en tierra, y aéreos que atacan zonas inaccesibles. Un orquestador central asigna misiones, resuelve conflictos de tareas duplicadas y monitorea el estado local del incendio.

# Roadmap
## World engine
- [X] Generación de biomas mediante Wave Function Collapse (WFC): Crear un generador de mapas que cree patrones de bosque, lagos y claros de forma coherente.
- [ ] Simulador de propagación "Ignis":
    - [ ] Implementar algoritmo de fuego determinista basado en vecinos (Von Neumann o Moore).
    - [ ] Inyectar modificadores ambientales: Velocidad/dirección del viento y niveles de humedad.
- [ ] Tick System: Implementar el motor de tiempo por pasos (ticks) configurable para la simulación.

## Infraestructura
- [ ] Caja Negra (Logging): Implementar un logger de eventos en tiempo real para capturar cada mensaje y cambio de estado del fuego.

## Respuesta (Agentes)
- [ ] Mecánicas de "Fog of War": Implementar el sistema de visión parcial. Los agentes solo conocen el estado del fuego en su radio de acción.
- [ ] Clases de unidades:
    - [ ] Dron (Observador): Alta movilidad, sin capacidad de extinción, pero limpia la "niebla de guerra".
    - [ ] Bombero (Terrestre): Movimiento lento, capacidad de contención en celdas adyacentes.
    - [ ] Camión (Terrestre): Ataque a zonas de alta intensidad o inaccesibles según el terreno.
- [ ] Sistema de Autonomía: Implementar la lógica para que los agentes soliciten misiones cuando estén ociosos.

## El Ojo en el Cielo (Orquestación)
- [ ] Orquestador Central "General":
    - [ ] Implementar asignación de tareas tipo Greedy (asignar el agente disponible más cercano al foco detectado).
    - [ ] Módulo de De-duplicación: Algoritmo para evitar que dos agentes sean enviados a la misma celda de incendio.
- [ ] Consolidación Estratégica: El orquestador debe generar un SupervisorDecision basado en los reportes de los drones.

## La Sala de Guerra (Visualización y KPI)
- [ ] Interfaz de Comando (GUI):
    - [ ] Renderizado del grid 256x256 en Pygame
    - [ ] Superposición de capas: Fuego, Humedad y Rutas de agentes.
- [ ] Tablero de Evaluación (KPI Post-Mortem):
    - [ ] Métrica de Victoria: Pantalla de resultados que muestre si se controló el $\ge 90\%$ del área.
    - [ ] Monitor de Telemetría: Gráfico de latencia de mensajes ($< 50\text{ms}$) y tasa de colisiones de tareas.

# Exito
1. Estabilidad: El sistema soporta un throughput de $\ge 500\text{ msg/s}$ sin perder paquetes.
2. Eficiencia: La tasa de tareas duplicadas es inferior al $2\%$.
3. Integración: Los agentes se comunican exclusivamente a través del bus de mensajes, no mediante acceso directo al estado global.

# Técnico
- Python 3.12