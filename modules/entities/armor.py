"""Класс брони"""
import pygame
import os
from modules.config import GOLD, BLUE, GRAY, WHITE
import modules.utils.fonts as fonts_module

def _ensure_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS


class Armor:
    def __init__(self, name, tier, defense, armor_type="normal", asset_path=None, element=None):
        self.name, self.tier, self.defense = name, tier, defense
        self.armor_type, self.element = armor_type, element
        self.asset_path = asset_path
        self.image = None
        self.image_size = None  # Храним размер текущей картинки
        self._load_image(120)

    def _load_image(self, size=120):
        # Если картинка уже загружена с нужным размером - не перезагружаем
        if self.image is not None and self.image_size == size:
            return
        # Пробуем разные пути для картинок
        possible_paths = [
            f"assets/images/{self.asset_path}" if self.asset_path else None,
            f"assets/{self.asset_path}" if self.asset_path else None,
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                try:
                    self.image = pygame.transform.scale(pygame.image.load(path), (size, size))
                    self.image_size = size
                    break
                except:
                    self.image = None

    def draw(self, screen, x, y, size=120):
        self._load_image(size)
        if self.image:
            screen.blit(self.image, (x, y))
        else:
            color = GOLD if self.tier == 4 else BLUE if self.tier >= 2 else GRAY
            pygame.draw.rect(screen, color, (x, y, size, size), border_radius=5)
            pygame.draw.rect(screen, WHITE, (x, y, size, size), 2, border_radius=5)

    def get_effect_text(self) -> str:
        if self.armor_type == "elemental" and self.element:
            element_names = {
                "fire": "Огонь", "water": "Вода", "electric": "Молния",
                "grass": "Природа", "ground": "Земля", "light": "Свет", "dark": "Тьма"
            }
            elem_name = element_names.get(self.element, self.element)
            return f"Защита: {self.defense} | Стихия: {elem_name}"
        return f"Защита: {self.defense}"

    def is_clicked(self, pos, x, y, size=120) -> bool:
        return x <= pos[0] <= x + size and y <= pos[1] <= y + size