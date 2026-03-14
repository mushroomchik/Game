"""Рендерер иконок"""
import pygame
from modules.config import WHITE, GOLD, BLACK, GREEN, RED, BLUE, ORANGE, PURPLE, YELLOW, LIGHT_GRAY

VALID_ICONS = {"sword", "fire", "heart", "shield", "crit", "star",
               "poison", "hero", "slime", "goblin", "skeleton", "ogre", "dragon", "dragon_baby", "inventory",
               "firefly", "light", "dark", "banshee", "ghost", "ghoul", "skeleton_sword", "skeleton_archer", "death"}

class IconRenderer:
    @staticmethod
    def draw_icon(screen, icon_type: str, x: int, y: int, size: int = 30):
        cx, cy = x + size//2, y + size//2
        if icon_type == "sword":
            pygame.draw.rect(screen, WHITE, (cx-3, y+5, 6, 20))
            pygame.draw.polygon(screen, WHITE, [(cx-3,y+5),(cx+3,y+5),(cx,y)])
            pygame.draw.rect(screen, GOLD, (cx-5, y+22, 10, 4))
        elif icon_type == "fire":
            pygame.draw.circle(screen, ORANGE, (cx, cy), size//2)
            pygame.draw.circle(screen, RED, (cx, cy-3), size//3)
            pygame.draw.circle(screen, YELLOW, (cx, cy-5), size//4)
        elif icon_type == "heart":
            r = size//4
            pygame.draw.circle(screen, GREEN, (cx-r, cy-r), r)
            pygame.draw.circle(screen, GREEN, (cx+r, cy-r), r)
            pygame.draw.polygon(screen, GREEN, [(x+8,cy-r),(x+size-8,cy-r),(cx,y+size-5)])
        elif icon_type == "shield":
            pts = [(x+8,y+5),(x+size-8,y+5),(x+size-8,y+size-10),(cx,y+size-3),(x+8,y+size-10)]
            pygame.draw.polygon(screen, BLUE, pts)
            pygame.draw.polygon(screen, WHITE, pts, 2)
        elif icon_type in ("crit", "star"):
            color = ORANGE if icon_type == "crit" else GOLD
            pts = []
            for i in range(5):
                a = i*72-90
                pts.append((cx+(size//2)*pygame.math.Vector2(1,0).rotate(a).x,
                           cy+(size//2)*pygame.math.Vector2(1,0).rotate(a).y))
                pts.append((cx+(size//4)*pygame.math.Vector2(1,0).rotate(a+36).x,
                           cy+(size//4)*pygame.math.Vector2(1,0).rotate(a+36).y))
            pygame.draw.polygon(screen, color, pts)
        elif icon_type == "poison":
            pygame.draw.circle(screen, PURPLE, (cx-5, cy-5), 6)
            pygame.draw.circle(screen, PURPLE, (cx+5, cy-5), 6)
            pygame.draw.rect(screen, PURPLE, (cx-3, cy, 6, 12))
        elif icon_type == "hero":
            pygame.draw.circle(screen, GREEN, (cx, cy), size//2)
            pygame.draw.circle(screen, WHITE, (cx, cy-5), size//4)
        elif icon_type == "slime":
            pygame.draw.ellipse(screen, GREEN, (x, y+5, size, size-5))
            pygame.draw.circle(screen, BLACK, (cx-5, cy), 4)
            pygame.draw.circle(screen, BLACK, (cx+5, cy), 4)
        elif icon_type == "goblin":
            pygame.draw.circle(screen, GREEN, (cx, cy), size//2)
            pygame.draw.circle(screen, RED, (cx-4, cy-2), 3)
            pygame.draw.circle(screen, RED, (cx+4, cy-2), 3)
        elif icon_type == "dragon":
            pygame.draw.circle(screen, RED, (cx, cy), size//2)
            pygame.draw.polygon(screen, RED, [(cx,y),(x-5,y+10),(x+5,y+10)])
            pygame.draw.circle(screen, YELLOW, (cx-4, cy-2), 3)
            pygame.draw.circle(screen, YELLOW, (cx+4, cy-2), 3)
        elif icon_type == "dragon_baby":
            pygame.draw.ellipse(screen, ORANGE, (x, y+5, size, size-5))
            pygame.draw.circle(screen, BLACK, (cx-5, cy), 4)
            pygame.draw.circle(screen, BLACK, (cx+5, cy), 4)
        elif icon_type == "inventory":
            # Иконка инвентаря (рюкзак)
            pygame.draw.rect(screen, BLUE, (x + 5, y + 5, size - 10, size - 10), border_radius=3)
            pygame.draw.line(screen, WHITE, (x + size//2, y + 8), (x + size//2, y + size - 8), 2)
            pygame.draw.line(screen, WHITE, (x + 8, y + size//2), (x + size - 8, y + size//2), 2)
        elif icon_type == "firefly":
            # Светлячок - маленькая светящаяся точка
            pygame.draw.circle(screen, YELLOW, (cx, cy), size//3)
            pygame.draw.circle(screen, (255, 255, 150), (cx, cy), size//4)
        elif icon_type == "light":
            # Свет - солнечные лучи
            pygame.draw.circle(screen, (255, 255, 200), (cx, cy), size//3)
            for angle in range(0, 360, 45):
                rad = pygame.math.Vector2(1, 0).rotate(angle)
                pygame.draw.line(screen, (255, 255, 200), (cx, cy), (cx + rad.x * size//2, cy + rad.y * size//2), 2)
        elif icon_type == "dark":
            # Тьма - тёмная сфера с фиолетовым оттенком
            pygame.draw.circle(screen, (60, 0, 80), (cx, cy), size//2)
            pygame.draw.circle(screen, (100, 0, 140), (cx, cy), size//3)
        elif icon_type == "banshee":
            # Банши - бледный женский силуэт
            pygame.draw.circle(screen, (200, 200, 220), (cx, cy), size//3)
            pygame.draw.line(screen, (180, 180, 200), (cx, cy + size//4), (cx, cy + size//2), 2)
        elif icon_type == "ghost":
            # Призрак - полупрозрачный силуэт
            pygame.draw.arc(screen, (200, 200, 255), (x, y, size, size//2), 3.14, 6.28, 2)
            pygame.draw.circle(screen, (200, 200, 255), (cx-4, cy-2), 3)
            pygame.draw.circle(screen, (200, 200, 255), (cx+4, cy-2), 3)
        elif icon_type == "ghoul":
            # Гуль - зеленовато-серое существо
            pygame.draw.ellipse(screen, (100, 120, 100), (x+5, y+5, size-10, size-5))
            pygame.draw.circle(screen, RED, (cx-5, cy), 3)
            pygame.draw.circle(screen, RED, (cx+5, cy), 3)
        elif icon_type == "skeleton_sword":
            # Скелет-мечник - белый череп
            pygame.draw.circle(screen, (220, 220, 220), (cx, cy), size//3)
            pygame.draw.circle(screen, BLACK, (cx-4, cy-2), 2)
            pygame.draw.circle(screen, BLACK, (cx+4, cy-2), 2)
            pygame.draw.rect(screen, (180, 180, 180), (cx-1, cy+2, 2, size//3))
        elif icon_type == "skeleton_archer":
            # Скелет-лучник - белый череп с дугой
            pygame.draw.circle(screen, (220, 220, 220), (cx, cy), size//3)
            pygame.draw.circle(screen, BLACK, (cx-4, cy-2), 2)
            pygame.draw.circle(screen, BLACK, (cx+4, cy-2), 2)
            pygame.draw.arc(screen, (180, 180, 180), (x+size//4, y, size//2, size), 4.71, 1.57, 2)
        elif icon_type == "death":
            # Смерть - черный плащ с капюшоном
            pygame.draw.polygon(screen, (20, 20, 20), [(cx, y), (x, y+size), (x+size, y+size)])
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), size//5)
        # Остальные иконки по аналогии...

    @staticmethod
    def draw_gold_icon(screen, x: int, y: int, size: int = 25):
        cx, cy = x+size//2, y+size//2
        pygame.draw.circle(screen, GOLD, (cx, cy), size//2)
        pygame.draw.circle(screen, BLACK, (cx, cy), size//2, 2)
        g = pygame.font.Font(None, size).render("G", True, BLACK)
        screen.blit(g, (cx-g.get_width()//2, cy-g.get_height()//2))

    @staticmethod
    def draw_type_icon(screen, damage_type: str, x: int, y: int, size: int = 16):
        """Отрисовка маленькой иконки типа урона"""
        icon_map = {"normal":"sword","fire":"fire","water":"shield","electric":"crit","grass":"heart","ground":"shield","light":"light","dark":"dark"}
        IconRenderer.draw_icon(screen, icon_map.get(damage_type, "sword"), x, y, size)