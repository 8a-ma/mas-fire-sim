class Pattern:
    VALID_PATTERN: list = [
        {
            'type': 'grass',
            'icon': '🌿',
            'rules': ['grass', 'mountain'],
            'color': '#1A7824'
        },
        {
            'type': 'water',
            'icon': '💧',
            'rules': ['water', 'grass'],
            'color': '#2FD6D4'
        },
        {
            'type': 'mountain',
            'icon': '🏔️',
            'rules': ['grass', 'mountain'],
            'color': '#ffffff'
        }
    ]