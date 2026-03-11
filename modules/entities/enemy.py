"""Класс врага"""
import pygame
import random
import os
from modules.config import RED, WHITE, TYPE_EFFECTIVENESS, TYPE_NAMES
import modules.utils.fonts as fonts_module
from modules.utils import IconRenderer

def _ensure_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS


class Enemy:
    def __init__(self, name, hp, damage_range, image_path=None, special_ability=None,
                 icon_type="slime", enemy_type="normal", damage_type="normal"):
        self.enemy_type = enemy_type
        self.damage_type = damage_type
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage_range = damage_range
        self.image_path = image_path
        self.image = None
        self.special_ability = special_ability
        self.icon_type = icon_type
        self.block = 0
        self.dead = False
        self._load_image()

    def _load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
                # Сохраняем оригинальный размер для разных контекстов
                self.image_full = pygame.transform.scale(self.image, (120, 120))
                self.image_small = pygame.transform.scale(self.image, (80, 80))
            except: 
                self.image = None
                self.image_full = None
                self.image_small = None

    def draw(self, screen, x, y):
        if hasattr(self, 'image_full') and self.image_full:
            screen.blit(self.image_full, (x, y))
        elif self.image:
            screen.blit(self.image, (x, y))
        else:
            pygame.draw.circle(screen, RED, (x + 60, y + 60), 50)
            pygame.draw.circle(screen, WHITE, (x + 60, y + 60), 50, 3)
            IconRenderer.draw_icon(screen, self.icon_type, x + 45, y + 45, 30)
        name_text = _ensure_fonts()['medium'].render(self.name, True, RED)
        screen.blit(name_text, (x + 60 - name_text.get_width() // 2, y + 130))

    def take_damage(self, amount: int, damage_type: str = "normal") -> int:
        """Применение урона с учётом типа атаки"""
        multiplier = self._get_effectiveness_multiplier(damage_type)
        effective_damage = int(amount * multiplier)
        actual_damage = max(0, effective_damage - self.block)
        self.block = 0
        self.hp = max(0, self.hp - actual_damage)
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return actual_damage

    def _get_effectiveness_multiplier(self, attack_type: str) -> float:
        """Расчёт множителя урона по типу"""
        enemy_category = getattr(self, 'enemy_type', 'normal')
        enemy_element = getattr(self, 'damage_type', 'normal')
        
        if enemy_category == "spirit":
            return TYPE_EFFECTIVENESS.get(attack_type, {}).get("spirit", 4.0)
        elif enemy_category == "elemental":
            return TYPE_EFFECTIVENESS.get(attack_type, {}).get("elemental", 0.25)
        
        return TYPE_EFFECTIVENESS.get(attack_type, {}).get(enemy_element, 1.0)

    def add_block(self, amount): self.block += amount

    def attack(self) -> tuple[int, str]:
        if self.dead: return 0, ""
        base_dmg = random.randint(self.damage_range[0], self.damage_range[1])
        if self.special_ability:
            if self.special_ability == "fire" and random.random() < 0.3:
                return base_dmg + 5, "ОГОНЬ!"
            elif self.special_ability == "poison" and random.random() < 0.3:
                return base_dmg, "ЯД!"
            elif self.special_ability == "freeze" and random.random() < 0.2:
                return base_dmg, "ЗАМОРОЗКА!"
        return base_dmg, ""

    def get_info_text(self) -> list[str]:
        """Информация о враге для тултипа"""
        info = [f"{self.name}", f"HP: {self.hp}/{self.max_hp}",
                f"Урон: {self.damage_range[0]}-{self.damage_range[1]}",
                f"Тип: {TYPE_NAMES.get(self.damage_type, 'Физический')}"]
        if self.enemy_type == "spirit":
            info.extend(["ДУХ: Иммунитет к обычным атакам!", "Слаб к элементальным!"])
        elif self.enemy_type == "elemental":
            info.extend(["ЭЛЕМЕНТАЛЬ: Иммунитет к стихиям!", "Слаб к обычным!"])
        info.append("Эффективность атак:")
        for attack_type in ["normal", "fire", "water", "electric", "grass", "ground"]:
            mult = self._get_effectiveness_multiplier(attack_type)
            name = TYPE_NAMES.get(attack_type, attack_type)
            if mult == 0: info.append(f"  {name}: ИММУНИТЕТ")
            elif mult >= 4: info.append(f"  {name}: x4")
            elif mult > 1: info.append(f"  {name}: x{mult}")
            elif mult < 1: info.append(f"  {name}: x{mult}")
            else: info.append(f"  {name}: x1 (обычный)")
        return info