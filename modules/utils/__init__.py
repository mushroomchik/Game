"""Утилиты"""
# ✅ Шрифты инициализируются в game.py после pygame.init()
from .fonts import get_fonts, create_fonts
from .icons import IconRenderer, VALID_ICONS
from .helpers import wrap_text
from .scaling import (init_scaling, scale, real_screen_width, real_screen_height, 
                      scale_pos, scale_size, get_scaled_font, get_render_surface, 
                      blit_to_screen, get_mouse_pos, offset_x, offset_y, BASE_WIDTH, BASE_HEIGHT)

# Временная заглушка — заполнится в game.py
FONTS = {}

__all__ = ['FONTS', 'get_fonts', 'create_fonts', 'IconRenderer', 'VALID_ICONS', 'wrap_text',
           'init_scaling', 'scale', 'real_screen_width', 'real_screen_height', 'scale_pos', 'scale_size', 
           'get_scaled_font', 'get_render_surface', 'blit_to_screen']