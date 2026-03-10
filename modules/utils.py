import pygame

pygame.init()
pygame.font.init()

from modules.settings import WHITE, GOLD, BLACK


# --- Шрифты ---
def create_fonts():
    font_names = ['arial.ttf', 'dejavusans.ttf', 'freesansbold.ttf', 'verdana.ttf']

    found_font = None
    for font_name in font_names:
        try:
            test_font = pygame.font.Font(font_name, 20)
            test_render = test_font.render("Тест", True, WHITE)
            found_font = font_name
            break
        except:
            continue

    if found_font:
        return {
            'large': pygame.font.Font(found_font, 52),
            'medium': pygame.font.Font(found_font, 36),
            'small': pygame.font.Font(found_font, 22),
            'tiny': pygame.font.Font(found_font, 16),
        }
    else:
        return {
            'large': pygame.font.Font(None, 52),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 16),
        }


FONTS = create_fonts()


# --- Иконки ---
class IconRenderer:
    """Рендерер иконок"""

    @staticmethod
    def draw_icon(screen, icon_type, x, y, size=30):
        from modules.settings import GREEN, RED, BLUE, ORANGE, PURPLE, YELLOW, LIGHT_GRAY, BLACK
        center_x = x + size // 2
        center_y = y + size // 2

        if icon_type == "sword":
            pygame.draw.rect(screen, WHITE, (center_x - 3, y + 5, 6, 20))
            pygame.draw.polygon(screen, WHITE, [(center_x - 3, y + 5), (center_x + 3, y + 5), (center_x, y)])
            pygame.draw.rect(screen, GOLD, (center_x - 5, y + 22, 10, 4))

        elif icon_type == "fire":
            pygame.draw.circle(screen, ORANGE, (center_x, center_y), size // 2)
            pygame.draw.circle(screen, RED, (center_x, center_y - 3), size // 3)
            pygame.draw.circle(screen, YELLOW, (center_x, center_y - 5), size // 4)

        elif icon_type == "heart":
            radius = size // 4
            pygame.draw.circle(screen, GREEN, (center_x - radius, center_y - radius), radius)
            pygame.draw.circle(screen, GREEN, (center_x + radius, center_y - radius), radius)
            pygame.draw.polygon(screen, GREEN, [(x + 8, center_y - radius), (x + size - 8, center_y - radius),
                                                (center_x, y + size - 5)])

        elif icon_type == "shield":
            shield_points = [(x + 8, y + 5), (x + size - 8, y + 5), (x + size - 8, y + size - 10),
                             (center_x, y + size - 3), (x + 8, y + size - 10)]
            pygame.draw.polygon(screen, BLUE, shield_points)
            pygame.draw.rect(screen, LIGHT_GRAY, (center_x - 3, center_y - 5, 6, 12))
            pygame.draw.polygon(screen, WHITE, shield_points, 2)

        elif icon_type == "crit":
            points = []
            for i in range(5):
                angle = i * 72 - 90
                outer_x = center_x + (size // 2) * pygame.math.Vector2(1, 0).rotate(angle).x
                outer_y = center_y + (size // 2) * pygame.math.Vector2(1, 0).rotate(angle).y
                points.append((outer_x, outer_y))
                inner_angle = angle + 36
                inner_x = center_x + (size // 4) * pygame.math.Vector2(1, 0).rotate(inner_angle).x
                inner_y = center_y + (size // 4) * pygame.math.Vector2(1, 0).rotate(inner_angle).y
                points.append((inner_x, inner_y))
            pygame.draw.polygon(screen, ORANGE, points)

        elif icon_type == "poison":
            pygame.draw.circle(screen, PURPLE, (center_x - 5, center_y - 5), 6)
            pygame.draw.circle(screen, PURPLE, (center_x + 5, center_y - 5), 6)
            pygame.draw.rect(screen, PURPLE, (center_x - 3, center_y, 6, 12))

        elif icon_type == "star":
            points = []
            for i in range(5):
                angle = i * 72 - 90
                outer_x = center_x + (size // 2) * pygame.math.Vector2(1, 0).rotate(angle).x
                outer_y = center_y + (size // 2) * pygame.math.Vector2(1, 0).rotate(angle).y
                points.append((outer_x, outer_y))
                inner_angle = angle + 36
                inner_x = center_x + (size // 4) * pygame.math.Vector2(1, 0).rotate(inner_angle).x
                inner_y = center_y + (size // 4) * pygame.math.Vector2(1, 0).rotate(inner_angle).y
                points.append((inner_x, inner_y))
            pygame.draw.polygon(screen, GOLD, points)

        elif icon_type == "hero":
            pygame.draw.circle(screen, GREEN, (center_x, center_y), size // 2)
            pygame.draw.circle(screen, WHITE, (center_x, center_y - 5), size // 4)
            pygame.draw.polygon(screen, GREEN, [(x, y + 10), (x + size, y + 10), (center_x, y)])

        elif icon_type == "slime":
            pygame.draw.ellipse(screen, GREEN, (x, y + 5, size, size - 5))
            pygame.draw.circle(screen, BLACK, (center_x - 5, center_y), 4)
            pygame.draw.circle(screen, BLACK, (center_x + 5, center_y), 4)
            pygame.draw.arc(screen, BLACK, (center_x - 5, center_y - 5, 10, 10), 3.14, 0, 2)

        elif icon_type == "goblin":
            pygame.draw.circle(screen, GREEN, (center_x, center_y), size // 2)
            pygame.draw.polygon(screen, GREEN, [(x, center_y), (x - 5, y), (x + 5, center_y - 5)])
            pygame.draw.polygon(screen, GREEN, [(x + size, center_y), (x + size + 5, y), (x + size - 5, center_y - 5)])
            pygame.draw.circle(screen, RED, (center_x - 4, center_y - 2), 3)
            pygame.draw.circle(screen, RED, (center_x + 4, center_y - 2), 3)

        elif icon_type == "skeleton":
            pygame.draw.circle(screen, WHITE, (center_x, center_y - 3), size // 3)
            pygame.draw.circle(screen, BLACK, (center_x - 3, center_y - 3), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 3, center_y - 3), 2)
            pygame.draw.rect(screen, WHITE, (center_x - 5, center_y + 5, 10, 8))

        elif icon_type == "ogre":
            pygame.draw.circle(screen, ORANGE, (center_x, center_y), size // 2)
            pygame.draw.circle(screen, BLACK, (center_x - 5, center_y - 2), 3)
            pygame.draw.circle(screen, BLACK, (center_x + 5, center_y - 2), 3)
            pygame.draw.rect(screen, BLACK, (center_x - 8, center_y + 5, 16, 4))
            pygame.draw.circle(screen, ORANGE, (x - 2, center_y - 5), 4)
            pygame.draw.circle(screen, ORANGE, (x + size + 2, center_y - 5), 4)

        elif icon_type == "dragon":
            pygame.draw.circle(screen, RED, (center_x, center_y), size // 2)
            pygame.draw.polygon(screen, RED, [(center_x, y), (x - 5, y + 10), (x + 5, y + 10)])
            pygame.draw.circle(screen, YELLOW, (center_x - 4, center_y - 2), 3)
            pygame.draw.circle(screen, YELLOW, (center_x + 4, center_y - 2), 3)
            pygame.draw.polygon(screen, RED,
                                [(x + size, center_y - 5), (x + size + 8, center_y - 10), (x + size + 5, center_y + 5)])

    @staticmethod
    def draw_gold_icon(screen, x, y, size=25):
        """ИСПРАВЛЕНО: Иконка золота - жёлтый круг с чёрной G"""
        center_x = x + size // 2
        center_y = y + size // 2

        # Жёлтый круг
        pygame.draw.circle(screen, GOLD, (center_x, center_y), size // 2)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), size // 2, 2)

        # Чёрная буква G
        font = pygame.font.Font(None, size)
        g_text = font.render("G", True, BLACK)
        screen.blit(g_text, (center_x - g_text.get_width() // 2, center_y - g_text.get_height() // 2))

    def draw_type_icon(screen, damage_type, x, y, size=16):
        """Отрисовка маленькой иконки типа урона"""
        icon_map = {
            "normal": "sword",
            "fire": "fire",
            "water": "shield",
            "electric": "crit",
            "grass": "heart",
            "ground": "shield"
        }

        icon_type = icon_map.get(damage_type, "sword")
        IconRenderer.draw_icon(screen, icon_type, x, y, size)