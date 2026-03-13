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
    0: {"name": "Старые доспехи", "defense": 0, "type": "normal", "asset": "armor_metal_0.png"},
    1: {"name": "Железная броня", "defense": 2, "type": "metal", "asset": "armor_metal_1.png"},
    2: [
        {"name": "Огненная броня", "defense": 1, "type": "elemental", "element": "fire", "asset": "armor_elemental_2_fire.png"},
        {"name": "Водяная броня", "defense": 1, "type": "elemental", "element": "water", "asset": "armor_elemental_2_water.png"},
        {"name": "Земляная броня", "defense": 1, "type": "elemental", "element": "ground", "asset": "armor_elemental_2_grass.png"},
    ],
    3: {"name": "Усиленная броня", "defense": 4, "type": "metal", "asset": "armor_metal_3.png"},
    4: {"name": "Легендарная броня", "defense": 5, "type": "legendary", "asset": "armor_legendary_4.png"},
    5: {"name": "Божественная броня", "defense": 10, "type": "divine", "asset": "divine_armor_5.png"},
}

# Улучшенные версии брони (для крафта из 3 одинаковых)
# Формат: (имя, тир, защита, тип, элемент, ассет)
ARMOR_UPGRADES = {
    ("Железная броня", 1): ("Усиленная броня", 3, 4, "metal", None, "armor_metal_3.png"),
    ("Огненная броня", 2): ("Огненная броня+", 3, 2, "elemental", "fire", "armor_elemental_2_fire.png"),
    ("Водяная броня", 2): ("Водяная броня+", 3, 2, "elemental", "water", "armor_elemental_2_water.png"),
    ("Земляная броня", 2): ("Земляная броня+", 3, 2, "elemental", "ground", "armor_elemental_2_grass.png"),
    ("Усиленная броня", 3): ("Усиленная броня+", 3, 8, "metal", None, "armor_metal_3.png"),
    ("Усиленная броня+", 3): ("Легендарная броня", 4, 5, "legendary", None, "armor_legendary_4.png"),
    ("Легендарная броня", 4): ("Божественная броня", 5, 10, "divine", None, "divine_armor_5.png"),
}

# Иконки
ICON_INVENTORY = "icon_inventory.png"