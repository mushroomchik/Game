"""Управление картой"""
import random
import pygame
from modules.config import MAP_COLS, MAP_NODE_TYPES, MAP_START_X, MAP_START_Y, NODE_SPACING_X, NODE_SPACING_Y
import modules.utils.fonts as fonts_module

def _ensure_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS



class MapNode:
    def __init__(self, col, row, node_type):
        self.col, self.row, self.type = col, row, node_type
        self.x = MAP_START_X + col * NODE_SPACING_X
        self.y = MAP_START_Y + row * NODE_SPACING_Y
        self.visited, self.active = False, False
        self.rect = pygame.Rect(self.x - 30, self.y - 30, 60, 60)

    def draw(self, screen):
        from modules.config import GREEN, GRAY, WHITE, BLACK, RED, ORANGE, GOLD, PURPLE, DARK_GRAY
        # Активный (можно выбрать) - зелёный
        # Посещённый - серый
        # Заблокированный (ещё не доступен) - тёмно-серый
        if self.active:
            color = GREEN
        elif self.visited:
            color = GRAY
        else:
            color = DARK_GRAY  # Заблокировано
        pygame.draw.circle(screen, color, (self.x, self.y), 30)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), 30, 2)
        # Текстовые иконки с цветами
        icon_colors = {
            "enemy": RED,
            "shop": ORANGE,
            "devil_shop": RED,  # Дьявольский магазин - красный
            "treasure": GOLD,
            "campfire": (255, 100, 0),  # Оранжево-красный
            "boss": PURPLE
        }
        icon_map = {"enemy": "[В]", "shop": "[М]", "devil_shop": "[М]", "treasure": "[С]", "campfire": "[К]", "boss": "[Б]"}
        text = icon_map.get(self.type, "?")
        icon_color = icon_colors.get(self.type, WHITE)
        text_surf = _ensure_fonts()['small'].render(text, True, icon_color)
        screen.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y - text_surf.get_height() // 2))


class MapManager:
    def __init__(self):
        self.node = None  # Один узел для боя
        self.current_col = 0
    
    @property
    def nodes(self):
        """Возвращает список узлов для рендерера"""
        return [self.node] if self.node else []

    def generate(self, floor: int = 1):
        """Создаём один узел для следующего боя"""
        self.node = MapNode(0, 1, "boss" if floor in [5, 10, 15] else "enemy")
        self.node.active = True
        self.node.visited = False
        self.current_col = 0

    def reset(self):
        """Сброс карты для новой игры"""
        self.node = None
        self.current_col = 0

    def get_active_nodes(self) -> list:
        return [self.node] if self.node and self.node.active else []

    def select_node(self, index: int) -> MapNode | None:
        if self.node and self.node.active:
            return self.node
        return None

    def proceed(self):
        """Переход к следующему бою"""
        if not self.node:
            return False
        self.node.visited = True
        self.node.active = False
        return True

    def is_at_end(self) -> bool:
        return False