"""Утилиты"""
# ✅ Шрифты инициализируются в game.py после pygame.init()
from .fonts import get_fonts, create_fonts
from .icons import IconRenderer, VALID_ICONS
from .helpers import wrap_text

# Временная заглушка — заполнится в game.py
FONTS = {}

__all__ = ['FONTS', 'get_fonts', 'create_fonts', 'IconRenderer', 'VALID_ICONS', 'wrap_text']