import pygame
import random
import os
from modules.settings import WHITE, BLACK, GRAY, GOLD, RED, DARK_GRAY, DICE_SIZE, ICON_SIZE
from modules.utils import IconRenderer, FONTS


# --- Кубик ---
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
        pygame.draw.rect(screen, BLACK if not self.used else DARK_GRAY,
                         (self.x, draw_y, self.size, self.size), 3, border_radius=8)

        if not self.used:
            self.draw_dots(screen, draw_y)

        if self.used:
            pygame.draw.line(screen, RED, (self.x, draw_y), (self.x + self.size, draw_y + self.size), 3)
            pygame.draw.line(screen, RED, (self.x + self.size, draw_y), (self.x, draw_y + self.size), 3)

    def draw_dots(self, screen, draw_y):
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
        if requirement == "any":
            return True
        elif requirement == "even":
            return self.value % 2 == 0
        elif requirement == "odd":
            return self.value % 2 == 1
        elif requirement == "high":
            return self.value >= 4
        elif requirement == "low":
            return self.value <= 3
        elif isinstance(requirement, int):
            return self.value == requirement
        elif isinstance(requirement, list):
            return self.value in requirement
        return False


# --- Враг ---
class Enemy:
    def __init__(self, name, hp, damage_range, image_path=None, special_ability=None,
                 icon_type="slime", enemy_type="normal", damage_type="normal"):

        self.enemy_type = enemy_type  # "normal", "spirit", "elemental"
        self.damage_type = damage_type  # "normal", "fire", "water", "electric"
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
        self.load_image()

    def load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
                self.image = pygame.transform.scale(self.image, (120, 120))
            except Exception as e:
                print(f"Не удалось загрузить изображение: {e}")
                self.image = None

    def draw(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))
        else:
            pygame.draw.circle(screen, RED, (x + 60, y + 60), 50)
            pygame.draw.circle(screen, WHITE, (x + 60, y + 60), 50, 3)
            pygame.draw.circle(screen, (100, 0, 0), (x + 60, y + 60), 45)
            IconRenderer.draw_icon(screen, self.icon_type, x + 45, y + 45, 30)

        name_text = FONTS['medium'].render(self.name, True, RED)
        screen.blit(name_text, (x + 60 - name_text.get_width() // 2, y + 130))

    def take_damage(self, amount):
        actual_damage = max(0, amount - self.block)
        self.hp -= actual_damage
        self.block = 0
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return actual_damage

    def add_block(self, amount):
        self.block += amount

    def attack(self):
        if self.dead:
            return 0, ""
        base_dmg = random.randint(self.damage_range[0], self.damage_range[1])

        if self.special_ability:
            if self.special_ability == "fire" and random.random() < 0.3:
                return base_dmg + 5, "ОГОНЬ!"
            elif self.special_ability == "poison" and random.random() < 0.3:
                return base_dmg, "ЯД!"
            elif self.special_ability == "freeze" and random.random() < 0.2:
                return base_dmg, "ЗАМОРОЗКА!"

        return base_dmg, ""


# --- Иконка персонажа ---
class CharacterIcon:
    def __init__(self, x, y, size=80, image_path=None, icon_type="hero"):
        self.x = x
        self.y = y
        self.size = size
        self.image_path = image_path
        self.icon_type = icon_type
        self.image = None
        self.load_image()

    def load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
            except:
                self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            from modules.settings import DARK_BLUE, WHITE
            pygame.draw.circle(screen, DARK_BLUE, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)
            pygame.draw.circle(screen, WHITE, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2, 3)
            IconRenderer.draw_icon(screen, self.icon_type, self.x + 25, self.y + 25, 30)