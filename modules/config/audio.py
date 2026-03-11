"""Аудио настройки"""
# Глобальный переключатель
SOUND_ENABLED = True
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Пути к звукам
SOUNDS = {
    "dice_roll": "assets/sounds/dice.wav",
    "card_activate": "assets/sounds/cast.wav",
    "enemy_hit": "assets/sounds/hit.wav",
    "player_hit": "assets/sounds/oof.wav",
    "victory": "assets/sounds/win.wav",
    "defeat": "assets/sounds/lose.wav",
    "button_click": "assets/sounds/click.wav",
    "card_buy": "assets/sounds/coin.wav",
    "card_upgrade": "assets/sounds/upgrade.wav",
}

# Фоновая музыка
MUSIC = {
    "menu": "assets/music/menu.ogg",
    "map": "assets/music/map.ogg",
    "battle": "assets/music/battle.ogg",
    "boss": "assets/music/boss.ogg",
    "victory": "assets/music/victory.ogg",
}