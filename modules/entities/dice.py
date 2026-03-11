"""Класс кубика"""
import pygame
import random
from modules.config import GRAY, GOLD, WHITE, BLACK, RED, DICE_SIZE

class Dice:
    def __init__(self, x, y, size=DICE_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.value = 1
        self.used = False
        self.selected = False
        self.roll_animation = 0

    def roll(self):
        self.value = random.randint(1, 6)
        self.used = False
        self.selected = False
        self.roll_animation = 15

    def draw(self, screen):
        draw_y = self.y
        if self.roll_animation > 0:
            draw_y += random.randint(-3, 3)
            self.roll_animation -= 1
        color = GRAY if self.used else GOLD if self.selected else WHITE
        pygame.draw.rect(screen, color, (self.x, draw_y, self.size, self.size), border_radius=8)
        pygame.draw.rect(screen, BLACK if not self.used else GRAY,
                        (self.x, draw_y, self.size, self.size), 3, border_radius=8)
        if not self.used:
            self._draw_dots(screen, draw_y)
        if self.used:
            pygame.draw.line(screen, RED, (self.x, draw_y), (self.x + self.size, draw_y + self.size), 3)
            pygame.draw.line(screen, RED, (self.x + self.size, draw_y), (self.x, draw_y + self.size), 3)

    def _draw_dots(self, screen, draw_y):
        dot_radius = self.size // 10
        center_x = self.x + self.size // 2
        center_y = draw_y + self.size // 2
        offset = self.size // 4
        dot_positions = {
            1: [(0, 0)],
            2: [(-offset, -offset), (offset, offset)],
            3: [(-offset, -offset), (0, 0), (offset, offset)],
            4: [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)],
            5: [(-offset, -offset), (offset, -offset), (0, 0), (-offset, offset), (offset, offset)],
            6: [(-offset, -offset), (offset, -offset), (-offset, 0), (offset, 0), (-offset, offset), (offset, offset)]
        }
        for dx, dy in dot_positions.get(self.value, []):
            pygame.draw.circle(screen, BLACK, (center_x + dx, center_y + dy), dot_radius)

    def is_clicked(self, pos):
        return (self.x <= pos[0] <= self.x + self.size and
                self.y <= pos[1] <= self.y + self.size)

    def can_be_used(self, requirement):
        if requirement == "any": return True
        if requirement == "even": return self.value % 2 == 0
        if requirement == "odd": return self.value % 2 == 1
        if requirement == "high": return self.value >= 4
        if requirement == "low": return self.value <= 3
        if isinstance(requirement, int): return self.value == requirement
        if isinstance(requirement, list): return self.value in requirement
        return False