"""Настройки карты и этапов"""
# Этапы (регионы)
STAGES = {
    1: {"name": "Гладиаторская арена", "floors": range(1, 6), "theme": "arena"},
    2: {"name": "Лес", "floors": range(6, 11), "theme": "forest"},
    3: {"name": "Озеро", "floors": range(11, 16), "theme": "water"},
    4: {"name": "Пещера", "floors": range(16, 21), "theme": "fire"},
    5: {"name": "Кладбище", "floors": range(21, 26), "theme": "dark"},
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
    "arena": {
        "name": "Гладиаторская арена",
        "theme": "arena",
        "enemies": [
            ("Гладиатор без оружия", 14, 2, 5, "gladiator_hands", "normal"),
            ("Гладиатор со щитом", 18, 3, 6, "gladiator_shield", "normal"),
            ("Гладиатор с мечом", 20, 4, 7, "gladiator_sword", "normal"),
            ("Опытный гладиатор", 28, 5, 9, "gladiator_sword_shield", "normal"),
        ],
        "boss": ("Гладиатор-чемпион", 55, 7, 12, "gladiator_champion", "normal"),
    },
    "forest": {
        "name": "Лес",
        "theme": "forest",
        "enemies": [
            ("Слизень", 12, 2, 4, "slime", "normal"),
            ("Гоблин", 15, 3, 5, "goblin", "normal"),
            ("Волк", 18, 4, 6, "wolf", "normal"),
            ("Древень", 25, 5, 8, "treant", "grass"),
            ("Светлячок", 20, 4, 7, "firefly", "light"),
            ("Теневой волк", 22, 5, 8, "wolf", "dark"),
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
            ("Лунная черепаха", 40, 5, 9, "turtle", "light"),
            ("Морской призрак", 38, 7, 11, "water_spirit", "dark"),
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
            ("Дракончик", 30, 9, 14, "dragon_baby", "fire"),
            ("Световой элементаль", 35, 8, 12, "fire_spirit", "light"),
            ("Теневой голем", 42, 9, 14, "lava_golem", "dark"),
        ],
        "boss": ("Древний дракон", 120, 14, 20, "fire_dragon", "fire"),
    },
    "graveyard": {
        "name": "Кладбище",
        "theme": "dark",
        "enemies": [
            ("Банши", 30, 7, 12, "banshee", "dark"),
            ("Призрак", 25, 6, 10, "ghost", "dark"),
            ("Гуль", 35, 8, 14, "ghoul", "dark"),
            ("Скелет-мечник", 28, 9, 15, "skeleton_sword", "dark"),
            ("Скелет-лучник", 22, 10, 16, "skeleton_archer", "dark"),
        ],
        "boss": ("Смерть", 150, 18, 28, "death", "dark"),
    },
}

def get_location_by_floor(floor: int) -> str:
    """Получить ключ локации по этажу"""
    if floor <= 5:
        return "arena"
    elif floor <= 10:
        return "forest"
    elif floor <= 15:
        return "water"
    elif floor <= 20:
        return "fire"
    else:
        return "graveyard"

def get_stage_by_floor(floor: int) -> int:
    """Получить номер этапа (1-5) по этажу"""
    if floor <= 5:
        return 1
    elif floor <= 10:
        return 2
    elif floor <= 15:
        return 3
    elif floor <= 20:
        return 4
    else:
        return 5

def get_boss_floor(stage: int) -> int:
    """Получить этаж босса для этапа"""
    # Этап 1: босс на 5, этап 2: босс на 10, и т.д.
    return stage * 5