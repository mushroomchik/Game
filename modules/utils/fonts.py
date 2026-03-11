"""Система шрифтов с безопасной инициализацией"""
import pygame

# Глобальный кэш шрифтов (заполняется при первом вызове)
_FONTS_CACHE = None

def create_fonts():
    """Создание словаря шрифтов с безопасной инициализацией"""
    # ✅ Гарантируем инициализацию шрифтов
    if not pygame.font.get_init():
        pygame.font.init()

    font_names = ['arial.ttf', 'dejavusans.ttf', 'freesansbold.ttf', 'verdana.ttf', None]
    found_font = None

    for font_name in font_names:
        try:
            # Пробуем создать тестовый шрифт
            test_font = pygame.font.Font(font_name, 20)
            test_render = test_font.render("Т", True, (255, 255, 255))
            found_font = font_name
            break
        except (pygame.error, OSError, FileNotFoundError):
            continue

    # Создаём словари шрифтов разных размеров
    sizes = {'large': 52, 'medium': 36, 'small': 22, 'tiny': 16}

    if found_font:
        return {name: pygame.font.Font(found_font, size) for name, size in sizes.items()}
    else:
        # Фоллбэк на системный шрифт (None)
        return {name: pygame.font.Font(None, size) for name, size in sizes.items()}

def get_fonts():
    """
    Безопасное получение шрифтов.
    Вызывайте ПОСЛЕ pygame.init() в main.py
    """
    global _FONTS_CACHE
    if _FONTS_CACHE is None:
        _FONTS_CACHE = create_fonts()
    return _FONTS_CACHE

# ✅ НЕ создаём шрифты при импорте!
# FONTS = create_fonts()  # ← УДАЛИТЬ эту строку
FONTS = {}  # ← Временная заглушка, заполнится в game.py