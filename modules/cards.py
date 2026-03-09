import pygame
from modules.settings import CARD_BORDER, WHITE, LIGHT_GRAY, YELLOW, GREEN, BLACK, DARK_GRAY, GRAY, GOLD, RED, ORANGE, \
    CARD_WIDTH, CARD_HEIGHT,BLUE
from modules.utils import IconRenderer, FONTS


class AbilityCard:
    """Карта способности"""

    def __init__(self, name, description, dice_requirement, dice_cost, effect_type,
                 effect_value, color, icon_type="sword", price=10, tier=0, damage_type="normal"):
        self.damage_type = damage_type  # ✅ Новый параметр
        self.name = name
        self.description = description
        self.dice_requirement = dice_requirement
        self.dice_cost = dice_cost
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.color = color
        self.icon_type = icon_type
        self.price = price
        self.tier = tier
        self.x = 0
        self.y = 0
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        self.hovered = False
        self.assigned_dice = []
        self.used_this_turn = False

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_sell_price(self):
        from modules.settings import SELL_PRICE_MULTIPLIER
        if self.tier >= 4:
            return 0
        return max(1, int(self.price * SELL_PRICE_MULTIPLIER))

    def get_tier_color(self):
        tier_colors = {
            0: LIGHT_GRAY,
            1: GREEN,
            2: BLUE,
            3: ORANGE,
            4: GOLD,
        }
        return tier_colors.get(self.tier, WHITE)

    def draw(self, screen, show_price=False, price_type="sell", player_gold=0):
        if self.used_this_turn:
            color = GRAY
        else:
            color = self.color if not self.hovered else tuple(min(255, c + 30) for c in self.color)
            if len(self.assigned_dice) >= self.dice_cost:
                color = GREEN

        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=10)

        tier_color = self.get_tier_color()
        pygame.draw.rect(screen, tier_color if not self.hovered else WHITE,
                         (self.x, self.y, self.width, self.height), 2, border_radius=10)

        icon_bg_x = self.x + self.width // 2 - 20
        icon_bg_y = self.y + 8
        pygame.draw.rect(screen, DARK_GRAY, (icon_bg_x, icon_bg_y, 40, 40), border_radius=8)
        IconRenderer.draw_icon(screen, self.icon_type, icon_bg_x + 5, icon_bg_y + 5, 30)

        name_text = FONTS['small'].render(self.name, True, WHITE)
        screen.blit(name_text, (self.x + 10, self.y + 55))

        req_text = self.get_requirement_text()
        req_surface = FONTS['tiny'].render(f"Треб: {req_text}", True, YELLOW)
        screen.blit(req_surface, (self.x + 10, self.y + 78))

        cost_text = FONTS['tiny'].render(f"Кубиков: {self.dice_cost}", True, LIGHT_GRAY)
        screen.blit(cost_text, (self.x + 10, self.y + 95))

        desc_lines = self.wrap_text(self.description, 14)
        for i, line in enumerate(desc_lines[:2]):
            desc_surface = FONTS['tiny'].render(line, True, WHITE)
            screen.blit(desc_surface, (self.x + 10, self.y + 115 + i * 16))

        for i, dice_val in enumerate(self.assigned_dice):
            pygame.draw.circle(screen, WHITE, (self.x + self.width - 15 - i * 22, self.y + 165), 9)
            pygame.draw.circle(screen, BLACK, (self.x + self.width - 15 - i * 22, self.y + 165), 7, 2)
            val_text = FONTS['tiny'].render(str(dice_val), True, BLACK)
            screen.blit(val_text, (self.x + self.width - 18 - i * 22, self.y + 160))

        if len(self.assigned_dice) >= self.dice_cost and not self.used_this_turn:
            pygame.draw.circle(screen, GREEN, (self.x + self.width - 12, self.y + 12), 7)

        if show_price:
            if price_type == "buy":
                price_value = self.price
                if player_gold >= price_value:
                    price_color = GREEN
                else:
                    price_color = RED
                price_label = "Цена:"
            else:
                price_value = self.get_sell_price()
                price_color = ORANGE
                price_label = "Продать:"

            price_text = FONTS['tiny'].render(f"{price_label} {price_value}", True, price_color)
            screen.blit(price_text, (self.x + 10, self.y + 145))
            IconRenderer.draw_gold_icon(screen, self.x + 105, self.y + 143, 18)

        if self.used_this_turn:
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x + self.width, self.y + self.height), 3)
            pygame.draw.line(screen, RED, (self.x + self.width, self.y), (self.x, self.y + self.height), 3)
            used_text = FONTS['tiny'].render("Использовано", True, RED)
            screen.blit(used_text, (self.x + self.width // 2 - used_text.get_width() // 2, self.y + self.height // 2))

        if self.hovered and not self.used_this_turn:
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 2,
                                             self.width + 4, self.height + 4), 1, border_radius=12)

    def get_requirement_text(self):
        req_map = {"any": "Любой", "even": "Чётный", "odd": "Нечётный", "high": "4+", "low": "1-3"}
        if isinstance(self.dice_requirement, list):
            return f"({','.join(map(str, self.dice_requirement))})"
        elif isinstance(self.dice_requirement, int):
            return str(self.dice_requirement)
        return req_map.get(self.dice_requirement, "?")

    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + word) <= max_chars:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def is_clicked(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height and
                not self.used_this_turn)

    def check_hover(self, pos):
        self.hovered = self.is_clicked(pos) and not self.used_this_turn

    def can_activate(self):
        return len(self.assigned_dice) >= self.dice_cost and not self.used_this_turn

    def calculate_effect(self):
        base = self.effect_value
        dice_sum = sum(self.assigned_dice)

        if self.effect_type == "damage":
            return dice_sum + base
        elif self.effect_type == "heal":
            return (dice_sum + base) // 2
        elif self.effect_type == "block":
            return dice_sum
        elif self.effect_type == "vampirism":
            return {"damage": dice_sum + base, "heal": (dice_sum + base) // 2}
        elif self.effect_type == "omnipotent":
            return {"damage": dice_sum + base, "heal": (dice_sum + base) // 3}
        elif self.effect_type == "special":
            return {"dice_sum": dice_sum, "dice_count": len(self.assigned_dice)}
        return base

    def reset(self):
        self.assigned_dice = []

    def reset_turn(self):
        self.used_this_turn = False
        self.assigned_dice = []

    def mark_used(self):
        self.used_this_turn = True