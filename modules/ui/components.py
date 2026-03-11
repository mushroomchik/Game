"""Базовые UI компоненты"""
import pygame
# ✅ Импорт из НЕСКОЛЬКИХ модулей конфигурации
from modules.config.display import (
    DARK_GRAY, GREEN, ORANGE, RED, BLUE, CYAN, WHITE, BLACK, GOLD,
    # УДАЛИТЕ отсюда BUTTON_TEXT_PADDING — он в gameplay.py
)
from modules.config.gameplay import BUTTON_TEXT_PADDING  # ✅ Правильный источник
import modules.utils.fonts as fonts_module
from modules.utils import IconRenderer

# Получение шрифтов с безопасной инициализацией
def _ensure_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS

class HealthBar:
    """Полоска здоровья"""
    def __init__(self, x, y, width, height, max_hp, color=GREEN, show_block=True):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.max_hp, self.current_hp = max_hp, max_hp
        self.color, self.block, self.show_block = color, 0, show_block

    def update(self, hp: int, block: int = 0):
        self.current_hp, self.block = hp, block

    def draw(self, screen):
        # Фон
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height), border_radius=5)
        # HP
        hp_w = int((max(0, self.current_hp) / self.max_hp) * self.width)
        color = GREEN if self.current_hp > self.max_hp*0.5 else ORANGE if self.current_hp > self.max_hp*0.25 else RED
        pygame.draw.rect(screen, color, (self.x, self.y, hp_w, self.height), border_radius=5)
        # Блок (отдельная полоска справа)
        if self.show_block and self.block > 0 and hp_w < self.width:
            block_w = min(self.width - hp_w, int((self.block / self.max_hp) * self.width))
            pygame.draw.rect(screen, BLUE, (self.x+hp_w+2, self.y, block_w, self.height), border_radius=5, width=2)
        # Рамка
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=5)
        # Текст
        hp_text = _ensure_fonts()['small'].render(f"{max(0, self.current_hp)}/{self.max_hp}", True, WHITE)
        screen.blit(hp_text, (self.x + self.width//2 - hp_text.get_width()//2,
                             self.y + self.height//2 - hp_text.get_height()//2))
        if self.show_block and self.block > 0:
            block_text = _ensure_fonts()['tiny'].render(f"Блок: {self.block}", True, CYAN)
            screen.blit(block_text, (self.x + self.width + 5, self.y))


class Button:
    """Кнопка с поддержкой иконок и анимацией"""
    def __init__(self, x, y, width, height, text, color=BLUE, icon_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color = text, color
        self.hover_color = tuple(min(255, c+30) for c in color)
        self.icon_type = icon_type
        self.is_hovered, self.enabled = False, True
        self._click_anim = 0

    def draw(self, screen, clicked=False):
        # Анимация нажатия
        offset = 3 if (clicked or self._click_anim > 0) else 0
        if self._click_anim > 0:
            self._click_anim -= 1

        color = self.hover_color if self.is_hovered else self.color
        if not self.enabled:
            color = (100, 100, 100)

        pygame.draw.rect(screen, color,
                        (self.rect.x+offset, self.rect.y+offset,
                         self.rect.width, self.rect.height), border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        # Текст с авто-уменьшением
        text_surf = self._render_fit_text(self.text, self.rect.width - BUTTON_TEXT_PADDING)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

        # Иконка справа
        if self.icon_type:
            IconRenderer.draw_icon(screen, self.icon_type,
                                  self.rect.right-35, self.rect.centery-12, 24)

    def _render_fit_text(self, text: str, max_width: int):
        surf = _ensure_fonts()['small'].render(text, True, WHITE)
        if surf.get_width() <= max_width:
            return surf
        return _ensure_fonts()['tiny'].render(text, True, WHITE)

    def is_clicked(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def trigger_click_animation(self):
        self._click_anim = 5


class Tooltip:
    """Универсальный тултип"""
    def __init__(self, font_key='tiny', bg_color=DARK_GRAY, border_color=GOLD):
        self.font_key, self.bg_color, self.border_color = font_key, bg_color, border_color
        self.lines = []

    def set_content(self, lines: list[str]):
        self.lines = lines

    def draw_at(self, screen, x: int, y: int):
        if not self.lines:
            return
        fonts = _ensure_fonts()
        # Расчёт размера
        max_w = max(fonts[self.font_key].render(l, True, WHITE).get_width() for l in self.lines)
        box_w, box_h = max_w + 20, len(self.lines) * 18 + 10
        # Позиция (не выходить за экран)
        x = min(x, screen.get_width() - box_w - 10)
        y = min(y, screen.get_height() - box_h - 10)
        # Фон
        pygame.draw.rect(screen, self.bg_color, (x, y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, self.border_color, (x, y, box_w, box_h), 2, border_radius=8)
        # Текст
        for i, line in enumerate(self.lines):
            screen.blit(fonts[self.font_key].render(line, True, WHITE), (x+10, y+5+i*18))