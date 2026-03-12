"""Конфигурация игры — центральный импорт"""
from .display import *
from .gameplay import *
from .cards_data import *
from .combat import *
from .map_config import *
from .assets import *
from .audio import *  # ✅ Добавляем аудио-конфиг

__all__ = [
    # display
    'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS',
    'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE', 'YELLOW', 'GRAY',
    'DARK_GRAY', 'LIGHT_GRAY', 'ORANGE', 'PURPLE', 'CYAN', 'GOLD',
    'DARK_BLUE', 'CARD_BG', 'CARD_BORDER', 'UI_POSITIONS',

    # gameplay
    'PLAYER_MAX_HP', 'DICE_COUNT', 'MAX_FLOOR', 'FLOOR_HEAL', 'CARDS_PER_TURN',
    'DICE_MILESTONES', 'STARTING_GOLD', 'GOLD_PER_VICTORY', 'GOLD_PER_BOSS',
    'SELL_PRICE_MULTIPLIER', 'UPGRADE_COSTS', 'REWARD_CHANCES', 'BOSS_FLOORS',

    # cards_data
    'TIER_0_CARDS', 'TIER_1_CARDS', 'TIER_2_CARDS', 'TIER_3_CARDS', 'TIER_4_CARDS',
    'CARD_UPGRADES', 'STARTING_INVENTORY', 'SHOP_CARDS',

    # combat
    'DAMAGE_TYPES', 'TYPE_EFFECTIVENESS', 'TYPE_NAMES', 'TYPE_ICONS',

    # map_config
    'STAGES', 'MAP_ROWS', 'MAP_COLS', 'NODE_SPACING_X', 'NODE_SPACING_Y',
    'MAP_START_X', 'MAP_START_Y', 'MAP_NODE_TYPES', 'LOCATIONS',
    'get_location_by_floor', 'get_stage_by_floor', 'get_boss_floor',

    # assets
    'ARMOR_TIERS', 'ELEMENT_COLORS', 'EFFECT_COLORS', 'ICON_INVENTORY','BUTTON_TEXT_PADDING',

'SOUND_ENABLED', 'SOUNDS', 'MUSIC_ENABLED', 'MUSIC_VOLUME', 'SFX_VOLUME', 'MUSIC',
]