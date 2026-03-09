import pygame
from modules.settings import CARD_BORDER, WHITE, LIGHT_GRAY, YELLOW, GREEN, BLACK, DARK_GRAY, GRAY, GOLD, RED, ORANGE, \
    CARD_WIDTH, CARD_HEIGHT,BLUE,CYAN,DARK_BLUE,SCREEN_WIDTH, SCREEN_HEIGHT,EFFECT_COLORS,ELEMENT_COLORS,PURPLE
from modules.utils import IconRenderer, FONTS


class AbilityCard:
    """Карта способности"""

    def __init__(self, name, description, dice_requirement, dice_cost, effect_type,
                 effect_value, color, icon_type="sword", price=10, tier=0, damage_type="normal"):
        self.name = name
        self.description = description
        self.dice_requirement = dice_requirement
        self.dice_cost = dice_cost
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.icon_type = icon_type
        self.price = price
        self.tier = tier
        self.damage_type = damage_type

        # === АВТОМАТИЧЕСКИЙ ВЫБОР ЦВЕТА ===
        if color == "auto":
            # Определяем цвет по типу эффекта или стихии
            if effect_type == "heal":
                self.color = EFFECT_COLORS["heal"]
            elif effect_type == "block":
                self.color = EFFECT_COLORS["block"]
            elif damage_type in ELEMENT_COLORS:
                self.color = ELEMENT_COLORS[damage_type]
            elif effect_type in EFFECT_COLORS:
                self.color = EFFECT_COLORS[effect_type]
            else:
                self.color = PURPLE  # По умолчанию
        else:
            self.color = color

        # === ПОЗИЦИЯ И РАЗМЕРЫ ===
        self.x = 0
        self.y = 0
        self.width = CARD_WIDTH  # ✅ ДОБАВЛЕНО
        self.height = CARD_HEIGHT  # ✅ ДОБАВЛЕНО

        # === СОСТОЯНИЕ ===
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

    def get_text_color(self, bg_color):
        """Возвращает контрастный цвет текста для фона"""
        # Считаем яркость фона (0-255)
        brightness = (bg_color[0] * 299 + bg_color[1] * 587 + bg_color[2] * 114) / 1000

        # Если фон тёмный — белый текст, если светлый — чёрный
        if brightness < 128:
            return WHITE
        else:
            return BLACK

        # Для особых случаев можно вернуть жёлтый для средних тонов
        # if 100 < brightness < 180:
        #     return YELLOW
        # return WHITE if brightness < 128 else BLACK

    def draw(self, screen, show_price=False, price_type="sell", player_gold=0):
        """Отрисовка карты с всплывающим описанием и единым цветом текста"""

        # === ФОН КАРТЫ ===
        if self.used_this_turn:
            color = GRAY
        else:
            color = self.color if not self.hovered else tuple(min(255, c + 30) for c in self.color)
            if len(self.assigned_dice) >= self.dice_cost:
                color = GREEN

        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=10)

        # === РАМКА ТИРА ===
        tier_color = self.get_tier_color()
        pygame.draw.rect(screen, tier_color if not self.hovered else WHITE,
                         (self.x, self.y, self.width, self.height), 2, border_radius=10)

        # === ИКОНКА ===
        icon_bg_x = self.x + self.width // 2 - 20
        icon_bg_y = self.y + 8
        pygame.draw.rect(screen, DARK_GRAY, (icon_bg_x, icon_bg_y, 40, 40), border_radius=8)
        IconRenderer.draw_icon(screen, self.icon_type, icon_bg_x + 5, icon_bg_y + 5, 30)

        # === НАЗВАНИЕ (единый белый цвет с тенью) ===
        name_text = FONTS['small'].render(self.name, True, WHITE)

        # Обрезаем название если не помещается
        max_name_width = self.width - 20
        display_name = self.name
        while name_text.get_width() > max_name_width and len(display_name) > 3:
            display_name = display_name[:-4] + "..."
            name_text = FONTS['small'].render(display_name, True, WHITE)

        # Тень для читаемости
        name_shadow = FONTS['small'].render(display_name, True, BLACK)
        screen.blit(name_shadow, (self.x + 11, self.y + 56))
        screen.blit(name_text, (self.x + 10, self.y + 55))

        # === ТРЕБОВАНИЯ (единый жёлтый цвет с тенью) ===
        req_text = self.get_requirement_text()
        req_surface = FONTS['tiny'].render(f"Треб: {req_text}", True, YELLOW)
        req_shadow = FONTS['tiny'].render(f"Треб: {req_text}", True, BLACK)
        screen.blit(req_shadow, (self.x + 11, self.y + 79))
        screen.blit(req_surface, (self.x + 10, self.y + 78))

        # === СТОИМОСТЬ В КУБИКАХ (единый светло-серый с тенью) ===
        cost_text = FONTS['tiny'].render(f"Кубиков: {self.dice_cost}", True, LIGHT_GRAY)
        cost_shadow = FONTS['tiny'].render(f"Кубиков: {self.dice_cost}", True, BLACK)
        screen.blit(cost_shadow, (self.x + 11, self.y + 96))
        screen.blit(cost_text, (self.x + 10, self.y + 95))

        # === ОПИСАНИЕ (с переносом, обрезкой и всплывающей подсказкой) ===
        desc_lines = self._wrap_text_smart(self.description, max_chars=20, max_lines=2)
        desc_y_start = self.y + 115

        for i, line in enumerate(desc_lines):
            display_text = line
            text_width = FONTS['tiny'].render(display_text, True, WHITE).get_width()
            max_text_width = self.width - 25

            # Обрезаем если не помещается
            while text_width > max_text_width and len(display_text) > 3:
                display_text = display_text[:-4] + "..."
                text_width = FONTS['tiny'].render(display_text, True, WHITE).get_width()

            # Тень + основной текст (ВСЕГДА БЕЛЫЙ)
            desc_shadow = FONTS['tiny'].render(display_text, True, BLACK)
            desc_surface = FONTS['tiny'].render(display_text, True, WHITE)

            text_y = desc_y_start + i * 18
            if text_y < self.y + self.height - 40:
                screen.blit(desc_shadow, (self.x + 11, text_y + 1))
                screen.blit(desc_surface, (self.x + 10, text_y))

        # === ВСПЛЫВАЮЩАЯ ПОДСКАЗКА С ПОЛНЫМ ОПИСАНИЕМ ===
        if self.hovered and not self.used_this_turn:
            self._draw_tooltip(screen)

        # === НАЗНАЧЕННЫЕ КУБИКИ ===
        for i, dice_val in enumerate(self.assigned_dice):
            dice_x = self.x + self.width - 15 - i * 22
            dice_y = self.y + 165

            if dice_x > self.x + 5:
                pygame.draw.circle(screen, WHITE, (dice_x, dice_y), 9)
                pygame.draw.circle(screen, BLACK, (dice_x, dice_y), 7, 2)
                val_text = FONTS['tiny'].render(str(dice_val), True, BLACK)
                screen.blit(val_text, (dice_x - 3, dice_y - 5))

        # === ИНДИКАТОР ГОТОВНОСТИ ===
        if len(self.assigned_dice) >= self.dice_cost and not self.used_this_turn:
            pygame.draw.circle(screen, GREEN, (self.x + self.width - 12, self.y + 12), 7)

        # === ЦЕНА ===
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
            price_shadow = FONTS['tiny'].render(f"{price_label} {price_value}", True, BLACK)

            price_y = self.y + 145
            if price_y < self.y + self.height - 20:
                screen.blit(price_shadow, (self.x + 11, price_y + 1))
                screen.blit(price_text, (self.x + 10, price_y))
                IconRenderer.draw_gold_icon(screen, self.x + 105, self.y + 143, 18)

        # === ПОМЕТКА "ИСПОЛЬЗОВАНО" ===
        if self.used_this_turn:
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x + self.width, self.y + self.height), 3)
            pygame.draw.line(screen, RED, (self.x + self.width, self.y), (self.x, self.y + self.height), 3)
            used_text = FONTS['tiny'].render("Использовано", True, RED)
            screen.blit(used_text, (self.x + self.width // 2 - used_text.get_width() // 2,
                                    self.y + self.height // 2))

        # === ПОДСВЕТКА ПРИ НАВЕДЕНИИ ===
        if self.hovered and not self.used_this_turn:
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 2,
                                             self.width + 4, self.height + 4), 2, border_radius=12)

    def _draw_tooltip(self, screen):
        """Всплывающая подсказка с полным описанием карты"""
        tooltip_lines = [
            f"📛 {self.name}",
            f"🎲 Стоимость: {self.dice_cost} куб.",
            f"📋 Требование: {self.get_requirement_text()}",
            "",
            "📖 Полное описание:",
        ]

        # Разбиваем полное описание на строки
        full_desc = self._wrap_text_smart(self.description, max_chars=40, max_lines=10)
        for line in full_desc:
            tooltip_lines.append(f"   {line}")

        tooltip_lines.append("")
        tooltip_lines.append(f"💰 Цена: {self.price}G | 📊 Тир: {self.tier}")

        if hasattr(self, 'damage_type'):
            type_icons = {"normal": "⚔️", "fire": "🔥", "water": "💧", "electric": "⚡"}
            tooltip_lines.append(f"🔮 Тип урона: {type_icons.get(self.damage_type, '⚔️')} {self.damage_type}")

        # Рассчитываем размер окна подсказки
        max_width = 0
        for line in tooltip_lines:
            text_width = FONTS['tiny'].render(line, True, WHITE).get_width()
            if text_width > max_width:
                max_width = text_width

        box_width = max_width + 20
        box_height = len(tooltip_lines) * 18 + 10

        # Позиция (над картой или под, чтобы не выходило за экран)
        tooltip_x = self.x
        tooltip_y = self.y - box_height - 10

        # Если не помещается сверху — показываем снизу
        if tooltip_y < 10:
            tooltip_y = self.y + self.height + 10

        # Если не помещается справа — сдвигаем влево
        if tooltip_x + box_width > SCREEN_WIDTH:
            tooltip_x = SCREEN_WIDTH - box_width - 10

        # Фон окна
        pygame.draw.rect(screen, DARK_BLUE, (tooltip_x, tooltip_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(screen, GOLD, (tooltip_x, tooltip_y, box_width, box_height), 2, border_radius=8)

        # Текст
        for i, line in enumerate(tooltip_lines):
            if line == "":
                continue
            elif "Полное описание:" in line:
                color = GOLD
            elif "📛" in line or "💰" in line or "📊" in line or "🔮" in line:
                color = CYAN
            else:
                color = WHITE

            text_surf = FONTS['tiny'].render(line, True, color)
            screen.blit(text_surf, (tooltip_x + 10, tooltip_y + 5 + i * 18))

    def _get_contrast_color(self, bg_color):
        """Возвращает контрастный цвет текста для фона"""
        # Считаем яркость фона (формула ITU-R BT.601)
        brightness = (bg_color[0] * 299 + bg_color[1] * 587 + bg_color[2] * 114) / 1000

        # Если фон тёмный — белый текст, если светлый — чёрный
        if brightness < 128:
            return WHITE
        else:
            return BLACK

    def _wrap_text_smart(self, text, max_chars=20, max_lines=2):
        """Умный перенос текста с ограничением по строкам"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if len(test_line.strip()) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
                if len(lines) >= max_lines:
                    break

        if current_line and len(lines) < max_lines:
            lines.append(current_line.strip())

        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if lines:
                lines[-1] = lines[-1][:max_chars - 3] + "..."

        return lines

    def get_requirement_text(self):
        req_map = {"any": "Любой", "even": "Чётный", "odd": "Нечётный", "high": "4+", "low": "1-3"}
        if isinstance(self.dice_requirement, list):
            return f"({','.join(map(str, self.dice_requirement))})"
        elif isinstance(self.dice_requirement, int):
            return str(self.dice_requirement)
        return req_map.get(self.dice_requirement, "?")

    def wrap_text(self, text, max_chars, max_lines=2):
        """Перенос текста с ограничением по строкам"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if len(test_line.strip()) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
                if len(lines) >= max_lines:
                    break

        if current_line and len(lines) < max_lines:
            lines.append(current_line.strip())

        # Обрезаем до max_lines и добавляем многоточие если нужно
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if lines:
                lines[-1] = lines[-1][:max_chars - 3] + "..."

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