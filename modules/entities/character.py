"""Иконка персонажа"""
import pygame
import os
from modules.config import DARK_BLUE, WHITE
from modules.utils import IconRenderer

class CharacterIcon:
    def __init__(self, x, y, size=80, image_path=None, icon_type="hero"):
        self.x, self.y, self.size = x, y, size
        self.image_path, self.icon_type = image_path, icon_type
        self.image = None
        self._load_image()

    def _load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.transform.scale(pygame.image.load(self.image_path), (self.size, self.size))
            except: self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.circle(screen, DARK_BLUE, (self.x + self.size//2, self.y + self.size//2), self.size//2)
            pygame.draw.circle(screen, WHITE, (self.x + self.size//2, self.y + self.size//2), self.size//2, 3)
            IconRenderer.draw_icon(screen, self.icon_type, self.x + 25, self.y + 25, 30)