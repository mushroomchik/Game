"""Клус карты способности"""
import pygame
from modules.config import (
    CARD_BORDER, WHITE, LIGHT_GRAY, YELLOW, GREEN, BLACK, DARK_GRAY, GRAY,
    GOLD, RED, ORANGE, CARD_WIDTH, CARD_HEIGHT, BLUE, CYAN, DARK_BLUE,
    SCREEN_WIDTH, SCREEN_HEIGHT, EFFECT_COLORS, ELEMENT_COLORS, PURPLE,
    BUTTON_TEXT_PADDING
)
import modules.utils.fonts as fonts_module
from modules.utils import IconRenderer, wrap_text
from .effects import calculate_card_effect


def _ensure_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS


class AbilityCard:
    def __init__(self, name, description, dice_requirement, dice_cost, effect_type,
                 effect_value, color, icon_type="sword", price=10, tier=0, damage_type="normal"):
        self.name, self.description = name, description
        self.dice_requirement, self.dice_cost = dice_requirement, dice_cost
        self.effect_type, self.effect_value = effect_type, effect_value
        self.icon_type, self.price = icon_type, price
        self.tier, self.damage_type = tier, damage_type

        # Авто-цвет
        if color == "auto":
            self.color = EFFECT_COLORS.get(effect_type) or ELEMENT_COLORS.get(damage_type) or PURPLE
        else:
            self.color = color

        # Позиция и состояние
        self.x, self.y = 0, 0
        self.width, self.height = CARD_WIDTH, CARD_HEIGHT
        self.hovered = False
        self.assigned_dice = []
        self.used_this_turn = False
        self.selected_for_battle = False  # Выбрана для боя в PRE_BATTLE

    def set_position(self, x, y):
        self.x, self.y = x, y

    def get_sell_price(self) -> int:
        from modules.config import SELL_PRICE_MULTIPLIER
        if self.tier >= 4: return 0
        return max(1, int(self.price * SELL_PRICE_MULTIPLIER))

    def get_tier_color(self):
        colors = {0: LIGHT_GRAY, 1: GREEN, 2: BLUE, 3: ORANGE, 4: GOLD}
        return colors.get(self.tier, WHITE)

    def draw(self, screen, show_price=False, price_type="sell", player_gold=0, force_available=False, draw_tooltip=True):
        # Фон
        if self.selected_for_battle:
            color = GREEN
        elif self.used_this_turn and not force_available:
            color = GRAY
        else:
            color = self.color if not self.hovered else tuple(min(255, c + 30) for c in self.color)
            if len(self.assigned_dice) >= self.dice_cost: color = GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=10)

        # Рамка тира
        tier_color = self.get_tier_color()
        pygame.draw.rect(screen, tier_color if not self.hovered else WHITE,
                         (self.x, self.y, self.width, self.height), 2, border_radius=10)

        # Иконка
        icon_bg = (self.x + self.width // 2 - 20, self.y + 8, 40, 40)
        pygame.draw.rect(screen, DARK_GRAY, icon_bg, border_radius=8)
        IconRenderer.draw_icon(screen, self.icon_type, icon_bg[0] + 5, icon_bg[1] + 5, 30)

        # Название (белый с тенью)
        name = self._truncate_text(self.name, self.width - 20, 'small')
        self._blit_with_shadow(screen, name, (self.x + 10, self.y + 55), WHITE)

        # Требования
        req = f"Треб: {self._get_requirement_text()}"
        self._blit_with_shadow(screen, req, (self.x + 10, self.y + 78), YELLOW)

        # Стоимость в кубиках
        cost = f"Кубиков: {self.dice_cost}"
        self._blit_with_shadow(screen, cost, (self.x + 10, self.y + 95), LIGHT_GRAY)

        # Описание
        desc_lines = wrap_text(self.description, max_chars=20, max_lines=2)
        for i, line in enumerate(desc_lines):
            y = self.y + 115 + i * 18
            if y < self.y + self.height - 40:
                self._blit_with_shadow(screen, self._truncate_text(line, self.width - 25, 'tiny'),
                                       (self.x + 10, y), WHITE)

        # Тултип при наведении (только если включено)
        if draw_tooltip and self.hovered:
            self._draw_tooltip(screen)

        # Назначенные кубики
        for i, val in enumerate(self.assigned_dice):
            dx = self.x + self.width - 15 - i * 22
            dy = self.y + 165
            if dx > self.x + 5:
                pygame.draw.circle(screen, WHITE, (dx, dy), 9)
                pygame.draw.circle(screen, BLACK, (dx, dy), 7, 2)
                self._blit_no_shadow(screen, str(val), (dx - 3, dy - 5), BLACK, 'tiny')

        # Индикатор готовности
        if len(self.assigned_dice) >= self.dice_cost and not self.used_this_turn:
            pygame.draw.circle(screen, GREEN, (self.x + self.width - 12, self.y + 12), 7)

        # Цена
        if show_price:
            self._draw_price(screen, price_type, player_gold)

        # Пометка "Использовано"
        if self.used_this_turn:
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x + self.width, self.y + self.height), 3)
            pygame.draw.line(screen, RED, (self.x + self.width, self.y), (self.x, self.y + self.height), 3)
            used = _ensure_fonts()['tiny'].render("Использовано", True, RED)
            screen.blit(used, (self.x + self.width // 2 - used.get_width() // 2,
                               self.y + self.height // 2))

        # Подсветка при наведении
        if self.hovered and not self.used_this_turn:
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 2,
                             border_radius=12)

    def _truncate_text(self, text: str, max_width: int, font_key: str) -> str:
        """Обрезка текста с многоточием"""
        while _ensure_fonts()[font_key].render(text + "...", True, WHITE).get_width() > max_width and len(text) > 3:
            text = text[:-4] + "..."
        return text

    def _blit_with_shadow(self, screen, text: str, pos: tuple, color: tuple, font_key: str = 'tiny'):
        """Отрисовка текста с чёрной тенью"""
        if isinstance(text, str):
            surface = _ensure_fonts()[font_key].render(text, True, color)
            shadow = _ensure_fonts()[font_key].render(text, True, BLACK)
        else:
            surface, shadow = text, _ensure_fonts()[font_key].render(text, True, BLACK)
        screen.blit(shadow, (pos[0] + 1, pos[1] + 1))
        screen.blit(surface, pos)

    def _blit_no_shadow(self, screen, text: str, pos: tuple, color: tuple, font_key: str = 'tiny'):
        screen.blit(_ensure_fonts()[font_key].render(text, True, color), pos)

    def _get_requirement_text(self) -> str:
        req_map = {"any": "Любой", "even": "Чётный", "odd": "Нечётный", "high": "4+", "low": "1-3"}
        if isinstance(self.dice_requirement, list):
            return f"({','.join(map(str, self.dice_requirement))})"
        if isinstance(self.dice_requirement, int):
            return str(self.dice_requirement)
        return req_map.get(self.dice_requirement, "?")

    def _draw_tooltip(self, screen):
        """Всплывающая подсказка"""
        type_names = {"normal": "Физический", "fire": "Огонь", "water": "Вода",
                      "electric": "Электричество", "grass": "Природа", "ground": "Земля"}
        lines = [
            f"{self.name}", f"Стоимость: {self.dice_cost} куб.",
            f"Требование: {self._get_requirement_text()}", "", "Полное описание:"
        ]
        lines.extend(f"   {l}" for l in wrap_text(self.description, 40, 10))
        lines.extend(["", f"Цена: {self.price}G | Тир: {self.tier}",
                      f"Тип урона: {type_names.get(self.damage_type, 'Физический')}"])

        # Расчёт размера
        max_w = max(_ensure_fonts()['tiny'].render(l, True, WHITE).get_width() for l in lines)
        box_w, box_h = max_w + 20, len(lines) * 18 + 10
        tx = min(self.x, SCREEN_WIDTH - box_w - 10)
        ty = self.y - box_h - 10 if self.y > box_h + 20 else self.y + self.height + 10

        # Фон
        pygame.draw.rect(screen, DARK_BLUE, (tx, ty, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, GOLD, (tx, ty, box_w, box_h), 2, border_radius=8)

        # Текст
        for i, line in enumerate(lines):
            color = GOLD if "Полное описание:" in line else CYAN if any(
                k in line for k in ["Цена:", "Тир:", "Тип урона:"]) else WHITE
            self._blit_no_shadow(screen, line, (tx + 10, ty + 5 + i * 18), color)

    def _draw_price(self, screen, price_type: str, player_gold: int):
        if price_type == "buy":
            value, color, label = self.price, GREEN if player_gold >= self.price else RED, "Цена:"
        else:
            value, color, label = self.get_sell_price(), ORANGE, "Продать:"
        text = f"{label} {value}"
        self._blit_with_shadow(screen, text, (self.x + 10, self.y + 145), color)
        IconRenderer.draw_gold_icon(screen, self.x + 105, self.y + 143, 18)

    def is_clicked(self, pos) -> bool:
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height and not self.used_this_turn)

    def check_hover(self, pos):
        self.hovered = self.is_clicked(pos)

    def can_activate(self) -> bool:
        return len(self.assigned_dice) >= self.dice_cost and not self.used_this_turn

    def calculate_effect(self) -> dict:
        return calculate_card_effect(self.effect_type, sum(self.assigned_dice),
                                     self.effect_value, self.description)

    def reset(self):
        self.assigned_dice = []

    def reset_turn(self):
        self.used_this_turn = False
        self.assigned_dice = []
        self.hovered = False
        # Не сбрасываем selected_for_battle здесь - это делается отдельно

    def mark_used(self):
        self.used_this_turn = True