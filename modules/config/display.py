"""Настройки отображения и цвета"""
# Экран
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 220, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 50)
LIGHT_GRAY = (180, 180, 180)
ORANGE = (255, 150, 50)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 200)
GOLD = (255, 215, 0)
DARK_BLUE = (30, 30, 60)
CARD_BG = (60, 60, 80)
CARD_BORDER = (120, 120, 150)

# Позиции UI (вынесены из game.py)
UI_POSITIONS = {
    'hero_icon': (50, 20),
    'hero_name': (140, 25),
    'hero_hp': (140, 50),
    'hero_gold': (140, 85),
    'enemy_icon': (950, 30),
    'enemy_name': (950, 160),
    'enemy_hp': (680, 50),
    'start_btn_center': SCREEN_WIDTH // 2,
    'restart_btn_center': SCREEN_WIDTH // 2,
    'dice_zone': (75, 220, 785, 140),
    'card_zone': (80, 480, 1040, 220),
    'end_turn_btn': (920, 350, 180, 50),
    'turn_text': (920, 310),
}

# Размеры
DICE_SIZE = 75
CARD_WIDTH = 150
CARD_HEIGHT = 190
ICON_SIZE = 35