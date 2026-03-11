"""Настройки карты и этапов"""
# Этапы (регионы)
STAGES = {
    1: {"name": "Lес", "floors": range(1, 6), "theme": "forest"},
    2: {"name": "Oзеро", "floors": range(6, 11), "theme": "water"},
    3: {"name": "Пещера", "floors": range(11, 16), "theme": "fire"},
}

# Карта
MAP_ROWS = 3
MAP_COLS = 5
NODE_SPACING_X = 200
NODE_SPACING_Y = 150
MAP_START_X = 100
MAP_START_Y = 200

# Типы узлов
MAP_NODE_TYPES = ["enemy", "shop", "treasure", "campfire", "boss"]