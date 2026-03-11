"""Игровые параметры и экономика"""
# Базовые статы
PLAYER_MAX_HP = 25
DICE_COUNT = 3
MAX_FLOOR = 15
FLOOR_HEAL = 3
CARDS_PER_TURN = 5

# Прогрессия
DICE_MILESTONES = [0, 3, 7, 12, 18]

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
BOSS_FLOORS = [5, 10, 15]

# UI настройки
BUTTON_TEXT_PADDING = 20
TOOLTIP_MAX_WIDTH = 300

