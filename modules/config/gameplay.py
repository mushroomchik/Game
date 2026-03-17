"""Игровые параметры и экономика"""
# Базовые статы
PLAYER_MAX_HP = 25
DICE_COUNT = 2
MAX_FLOOR = 25
FLOOR_HEAL = 3
CARDS_PER_TURN = 5

# Прогрессия - этажи, на которых даётся дополнительный кубик
DICE_MILESTONES = [0, 1, 3, 6, 10, 15, 20]

def get_dice_count_by_floor(floor: int) -> int:
    """Получить количество кубиков по этажу"""
    base_dice = 2
    extra = sum(1 for m in DICE_MILESTONES if floor > m)
    return base_dice + extra

# Экономика
STARTING_GOLD = 20
GOLD_PER_VICTORY = 20
GOLD_PER_BOSS = 75
SELL_PRICE_MULTIPLIER = 0.3

# Цены апгрейдов
UPGRADE_COSTS = {0: 20, 1: 40, 2: 70}

# Шансы наград по тирам
REWARD_CHANCES = {0: 40, 1: 40, 2: 20}

# Боссы
BOSS_FLOORS = [5, 10, 15, 20]

# UI настройки
BUTTON_TEXT_PADDING = 20
TOOLTIP_MAX_WIDTH = 300

