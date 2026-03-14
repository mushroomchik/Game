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
        self._load_image()

    def _load_image(self):
        # Пробуем разные пути для картинок
        possible_paths = [
            f"assets/images/{self.asset_path}" if self.asset_path else None,
            f"assets/{self.asset_path}" if self.asset_path else None,
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                try:
                    self.image = pygame.transform.scale(pygame.image.load(path), (120, 120))
                    break
                except:
                    self.image = None

    def draw(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))
        else:
            color = GOLD if self.tier == 4 else BLUE if self.tier >= 2 else GRAY
            pygame.draw.rect(screen, color, (x, y, 120, 120), border_radius=5)
            pygame.draw.rect(screen, WHITE, (x, y, 120, 120), 2, border_radius=5)

    def get_effect_text(self) -> str:
        if self.armor_type == "elemental" and self.element:
            element_names = {
                "fire": "Огонь", "water": "Вода", "electric": "Молния",
                "grass": "Природа", "ground": "Земля", "light": "Свет", "dark": "Тьма"
            }
            elem_name = element_names.get(self.element, self.element)
            return f"Защита: {self.defense} | Стихия: {elem_name}"
        return f"Защита: {self.defense}"

    def is_clicked(self, pos, x, y) -> bool:
        return x <= pos[0] <= x + 120 and y <= pos[1] <= y + 120