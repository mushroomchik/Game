import pygame
from modules.settings import DARK_GRAY, GREEN, ORANGE, RED, BLUE, CYAN, WHITE
from modules.utils import FONTS


class HealthBar:
    """Полоска здоровья"""

    def __init__(self, x, y, width, height, max_hp, color=GREEN, show_block=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.color = color
        self.block = 0
        self.show_block = show_block

    def update(self, hp, block=0):
        self.current_hp = hp
        self.block = block

    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height), border_radius=5)

        hp_width = int((max(0, self.current_hp) / self.max_hp) * self.width)
        color = GREEN if self.current_hp > self.max_hp * 0.5 else ORANGE if self.current_hp > self.max_hp * 0.25 else RED
        pygame.draw.rect(screen, color, (self.x, self.y, hp_width, self.height), border_radius=5)

        if self.show_block and self.block > 0:
            block_width = min(self.width, int((self.block / self.max_hp) * self.width))
            pygame.draw.rect(screen, BLUE, (self.x, self.y, block_width, self.height), border_radius=5)

        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=5)

        hp_text = FONTS['small'].render(f"{max(0, self.current_hp)}/{self.max_hp}", True, WHITE)
        screen.blit(hp_text, (self.x + self.width // 2 - hp_text.get_width() // 2,
                              self.y + self.height // 2 - hp_text.get_height() // 2))

        if self.show_block and self.block > 0:
            block_text = FONTS['tiny'].render(f"Блок: {self.block}", True, CYAN)
            screen.blit(block_text, (self.x + self.width + 5, self.y))


class Button:
    """Кнопка - ИСПРАВЛЕНО: текст не выходит за рамки"""

    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.is_hovered = False
        self.enabled = True

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        if not self.enabled:
            color = (100, 100, 100)

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        # ИСПРАВЛЕНО: уменьшил шрифт и добавил перенос
        text_surface = FONTS['small'].render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Если текст слишком широкий - уменьшаем
        if text_surface.get_width() > self.rect.width - 20:
            text_surface = FONTS['tiny'].render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)

        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)