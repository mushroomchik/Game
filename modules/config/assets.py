"""Ассеты: цвета, броня, иконки"""
# ✅ Явный импорт цветов из display.py
from .display import PURPLE, BLUE, GREEN, GOLD, ORANGE, RED, YELLOW, LIGHT_GRAY, CYAN, WHITE, DARK_BLUE

# Цвета стихий
ELEMENT_COLORS = {
    "normal": PURPLE,
    "fire": (255, 100, 50),
    "water": (50, 150, 255),
    "electric": (255, 220, 50),
    "grass": (100, 220, 100),
    "ground": (180, 120, 60),
}

# Цвета эффектов
EFFECT_COLORS = {
    "damage": PURPLE,
    "heal": (100, 220, 100),
    "block": (50, 150, 255),
    "vampirism": (180, 50, 180),
    "omnipotent": GOLD,
    "special": CYAN,
}

# Броня по тирам
ARMOR_TIERS = {
    0: {"name": "Старая одежда", "defense": 0, "type": "normal", "asset": "armor_metal_0.png"},
    1: {"name": "Железная броня", "defense": 2, "type": "metal", "asset": "armor_metal_1.png"},
    2: [
        {"name": "Огненная броня", "defense": 1, "type": "elemental", "element": "fire", "asset": "armor_elemental_2_fire.png"},
        {"name": "Водяная броня", "defense": 1, "type": "elemental", "element": "water", "asset": "armor_elemental_2_water.png"},
        {"name": "Земляная броня", "defense": 1, "type": "elemental", "element": "ground", "asset": "armor_elemental_2_grass.png"},
    ],
    3: {"name": "Усиленная броня", "defense": 4, "type": "metal", "asset": "armor_metal_3.png"},
    4: {"name": "Легендарная броня", "defense": 5, "type": "legendary", "asset": "armor_legendary_4.png"},
}

# Иконки
ICON_INVENTORY = "icon_inventory.png"