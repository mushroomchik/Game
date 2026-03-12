"""Настройки карты и этапов"""
# Этапы (регионы)
STAGES = {
    1: {"name": "Лес", "floors": range(1, 6), "theme": "forest"},
    2: {"name": "Озеро", "floors": range(6, 11), "theme": "water"},
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

# === ВРАГИ ПО ЛОКАЦИЯМ ===
# Каждая локация имеет своих врагов и босса
# Формат: (имя, базовое_HP, базовый_урон_мин, базовый_урон_макс, иконка, тип_урона)
LOCATIONS = {
    "forest": {
        "name": "Лес",
        "theme": "forest",
        "enemies": [
            ("Слизень", 12, 2, 4, "slime", "normal"),
            ("Гоблин", 15, 3, 5, "goblin", "normal"),
            ("Волк", 18, 4, 6, "wolf", "normal"),
            ("Древень", 25, 5, 8, "treant", "grass"),
        ],
        "boss": ("Лесной дух", 50, 6, 10, "forest_spirit", "grass"),
    },
    "water": {
        "name": "Озеро",
        "theme": "water",
        "enemies": [
            ("Водяной слайм", 20, 4, 6, "water_slime", "water"),
            ("Водяной дух", 22, 5, 7, "water_spirit", "water"),
            ("Рыбо-человек", 28, 6, 9, "fish_man", "water"),
            ("Нага", 32, 7, 10, "naga", "water"),
            ("Черепаха", 35, 4, 8, "turtle", "water"),
        ],
        "boss": ("Кракен", 80, 10, 15, "kraken", "water"),
    },
    "fire": {
        "name": "Пещера",
        "theme": "fire",
        "enemies": [
            ("Огненный слайм", 25, 5, 8, "fire_slime", "fire"),
            ("Огненный дух", 28, 6, 9, "fire_spirit", "fire"),
            ("Магмовый зверь", 32, 7, 10, "magma_beast", "fire"),
            ("Лавовый голем", 38, 8, 12, "lava_golem", "fire"),
            ("Дракончик", 30, 9, 14, "fire_dragon", "fire"),
        ],
        "boss": ("Древний дракон", 120, 14, 20, "fire_dragon", "fire"),
    },
}

def get_location_by_floor(floor: int) -> str:
    """Получить ключ локации по этажу"""
    if floor <= 5:
        return "forest"
    elif floor <= 10:
        return "water"
    else:
        return "fire"

def get_stage_by_floor(floor: int) -> int:
    """Получить номер этапа (1-3) по этажу"""
    if floor <= 5:
        return 1
    elif floor <= 10:
        return 2
    else:
        return 3

def get_boss_floor(stage: int) -> int:
    """Получить этаж босса для этапа"""
    return stage * 5