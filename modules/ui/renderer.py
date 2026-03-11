"""Рендерер игры"""
import pygame
from modules.config.display import *  # ✅ Все цвета
from modules.config.gameplay import *  # ✅ Константы геймплея
from modules.config.cards_data import CARD_UPGRADES
from modules.config.gameplay import UPGRADE_COSTS  # Для магазина
import modules.utils.fonts as fonts_module
from modules.utils import IconRenderer
from .components import HealthBar, Button, Tooltip

# Получение шрифтов с безопасной инициализацией
def _get_fonts():
    if not fonts_module.FONTS:
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()
    return fonts_module.FONTS

# Глобальная переменная FONTS которая лениво инициализируется
FONTS = None

def _ensure_fonts():
    global FONTS
    if FONTS is None:
        FONTS = _get_fonts()
    return FONTS

class GameRenderer:
    """Статический рендерер для всех экранов игры"""

    # =========================================================================
    # === ГЛАВНОЕ МЕНЮ ===
    # =========================================================================
    @staticmethod
    def draw_menu(screen, start_btn: Button):
        """Отрисовка главного меню"""
        screen.fill(DARK_BLUE)

        # Заголовок
        title = _ensure_fonts()['large'].render("Knight with Dice", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Подзаголовок
        subtitle = _ensure_fonts()['medium'].render("Карточная RPG", True, LIGHT_GRAY)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))

        # Кнопка старта
        start_btn.draw(screen)

        # Подсказка
        hint = _ensure_fonts()['tiny'].render("Кликните чтобы начать приключение", True, LIGHT_GRAY)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 330))

    # =========================================================================
    # === КАРТА ===
    # =========================================================================
    @staticmethod
    def draw_map(screen, nodes: list, floor: int, player_hp: int, max_hp: int,
                 gold: int, inventory_btn: Button, message: str = "", next_enemy=None):
        """Отрисовка карты приключений"""
        screen.fill(DARK_BLUE)

        # Заголовок
        title = _ensure_fonts()['large'].render("Карта приключений", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # Этап
        stage_name = GameRenderer._get_stage_name(floor)
        stage_text = _ensure_fonts()['medium'].render(stage_name, True, CYAN)
        screen.blit(stage_text, (SCREEN_WIDTH // 2 - stage_text.get_width() // 2, 75))

        # Узлы карты
        for node in nodes:
            node.draw(screen)

        # Информация о следующем враге
        if next_enemy:
            enemy_info_bg = pygame.Rect(SCREEN_WIDTH // 2 - 200, 450, 400, 180)
            pygame.draw.rect(screen, DARK_GRAY, enemy_info_bg, border_radius=10)
            pygame.draw.rect(screen, RED, enemy_info_bg, 2, border_radius=10)
            
            # Изображение врага из PNG
            enemy_img_x = SCREEN_WIDTH // 2 - 40
            enemy_img_y = 465
            if hasattr(next_enemy, 'image_small') and next_enemy.image_small:
                screen.blit(next_enemy.image_small, (enemy_img_x, enemy_img_y))
            elif next_enemy.image:
                screen.blit(next_enemy.image, (enemy_img_x, enemy_img_y))
            else:
                # Если нет изображения - рисую прямоугольник с именем
                pygame.draw.rect(screen, RED, (enemy_img_x, enemy_img_y, 80, 80), border_radius=5)
            
            enemy_title = _ensure_fonts()['medium'].render("Следующий враг:", True, RED)
            screen.blit(enemy_title, (SCREEN_WIDTH // 2 - enemy_title.get_width() // 2, 520))
            
            enemy_name = _ensure_fonts()['small'].render(next_enemy.name, True, WHITE)
            screen.blit(enemy_name, (SCREEN_WIDTH // 2 - enemy_name.get_width() // 2, 555))
            
            enemy_hp = _ensure_fonts()['small'].render(f"HP: {next_enemy.hp}/{next_enemy.max_hp}", True, GREEN)
            screen.blit(enemy_hp, (SCREEN_WIDTH // 2 - enemy_hp.get_width() // 2, 580))
            
            enemy_dmg = _ensure_fonts()['small'].render(f"Урон: {next_enemy.damage_range[0]}-{next_enemy.damage_range[1]}", True, YELLOW)
            screen.blit(enemy_dmg, (SCREEN_WIDTH // 2 - enemy_dmg.get_width() // 2, 600))

        # Информация игрока
        info = _ensure_fonts()['small'].render(
            f"Этаж: {floor}/{MAX_FLOOR} | HP: {player_hp}/{max_hp} | Золото: {gold}",
            True, WHITE
        )
        screen.blit(info, (20, 750))

        # Кнопка инвентаря
        inventory_btn.draw(screen)

        # Сообщение
        if message:
            msg = _ensure_fonts()['small'].render(message, True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 700))

    @staticmethod
    def _get_stage_name(floor: int) -> str:
        """Получение названия этапа по этажу"""
        if floor <= 5:
            return "Лесной регион (1-5)"
        elif floor <= 10:
            return "Озерный регион (6-10)"
        else:
            return "Огненная пещера (11-15)"

    @staticmethod
    def _draw_map_legend(screen):
        """Легенда карты"""
        legend_y = 780
        legends = [
            ("[В]", "Враг", WHITE),
            ("[М]", "Магазин", ORANGE),
            ("[С]", "Сокровище", GOLD),
            ("[К]", "Костер", RED),
            ("[Б]", "Босс", PURPLE),
        ]
        x = 200
        for icon, text, color in legends:
            icon_surf = _ensure_fonts()['tiny'].render(icon, True, color)
            text_surf = _ensure_fonts()['tiny'].render(text, True, LIGHT_GRAY)
            screen.blit(icon_surf, (x, legend_y))
            screen.blit(text_surf, (x + 25, legend_y))
            x += 120

    # =========================================================================
    # === ИНВЕНТАРЬ ===
    # =========================================================================
    @staticmethod
    def draw_inventory(screen, inventory_cards: list, inventory_armor: list,
                      equipped_armor, map_btn: Button, message: str = "",
                      armor_tooltip_visible=False, armor_tooltip_pos=(0,0), armor_tooltip_armor=None,
                      current_tab="cards", scroll=0):
        """Отрисовка экрана инвентаря с вкладками и скроллом"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок
        title = _ensure_fonts()['large'].render("Инвентарь", True, GOLD)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 50))

        # Вкладки
        cards_tab_rect = pygame.Rect(50, 120, 150, 40)
        armor_tab_rect = pygame.Rect(210, 120, 150, 40)

        # Фон вкладок
        for rect, tab_name, is_active in [
            (cards_tab_rect, "Карты", current_tab == "cards"),
            (armor_tab_rect, "Броня", current_tab == "armor")
        ]:
            color = GREEN if is_active else DARK_GRAY
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE if is_active else GRAY, rect, 2, border_radius=8)
            tab_text = _ensure_fonts()['medium'].render(tab_name, True, WHITE)
            text_x = rect.x + (rect.width - tab_text.get_width()) // 2
            text_y = rect.y + (rect.height - tab_text.get_height()) // 2
            screen.blit(tab_text, (text_x, text_y))

        # Контент вкладок
        if current_tab == "cards":
            # Карты со скроллом
            cards_per_row = 5
            card_start = scroll
            cards_visible = inventory_cards[card_start:card_start + 10]
            hovered_card = None
            # Сначала рисуем все карты без тултипов, запоминаем наведенную
            for i, card in enumerate(cards_visible):
                row = i // cards_per_row
                col = i % cards_per_row
                card.set_position(50 + col * 160, 180 + row * 200)
                card.check_hover(pygame.mouse.get_pos())
                if card.hovered:
                    hovered_card = card
                card.draw(screen, force_available=True, draw_tooltip=False)
            # Потом рисуем тултип только для наведенной карты (поверх всех)
            if hovered_card:
                hovered_card._draw_tooltip(screen)

            # Индикатор скролла
            if len(inventory_cards) > 10:
                max_scroll = len(inventory_cards) - 10
                scroll_bar_height = 150
                scroll_thumb_height = max(20, scroll_bar_height * 10 // len(inventory_cards))
                scroll_pos = int(scroll * (scroll_bar_height - scroll_thumb_height) / max(max_scroll, 1))
                pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH - 30, 180, 15, scroll_bar_height), border_radius=5)
                pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 30, 180 + scroll_pos, 15, scroll_thumb_height), border_radius=5)

        else:
            # Броня со скроллом
            armor_cols = 8
            armor_start = scroll
            armor_visible = inventory_armor[armor_start:armor_start + 16]
            for i, armor in enumerate(armor_visible):
                row = i // armor_cols
                col = i % armor_cols
                x = 50 + col * 100
                y = 180 + row * 80
                armor.draw(screen, x, y)
                if equipped_armor == armor:
                    pygame.draw.rect(screen, GREEN, (x - 2, y - 2, 54, 54), 2)
                # Обрезаем название если слишком длинное
                name_text = armor.name
                while len(name_text) > 6 and _ensure_fonts()['tiny'].render(name_text, True, WHITE).get_width() > 90:
                    name_text = name_text[:-1]
                if name_text != armor.name:
                    name_text = name_text + ".."
                name = _ensure_fonts()['tiny'].render(name_text, True, WHITE)
                name_x = x + (50 - name.get_width()) // 2
                screen.blit(name, (name_x, y + 55))

            # Индикатор скролла
            if len(inventory_armor) > 16:
                max_scroll = len(inventory_armor) - 16
                scroll_bar_height = 320
                scroll_thumb_height = max(20, scroll_bar_height * 16 // len(inventory_armor))
                scroll_pos = int(scroll * (scroll_bar_height - scroll_thumb_height) / max(max_scroll, 1))
                pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH - 30, 180, 15, scroll_bar_height), border_radius=5)
                pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 30, 180 + scroll_pos, 15, scroll_thumb_height), border_radius=5)

        # Тултип брони
        if armor_tooltip_visible and armor_tooltip_armor:
            GameRenderer._draw_armor_tooltip(screen, armor_tooltip_armor, armor_tooltip_pos)

        # Кнопка возврата
        map_btn.draw(screen)

        # Сообщение
        if message:
            msg = _ensure_fonts()['small'].render(message, True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 720))

    # =========================================================================
    # === ПОДГОТОВКА К БОЮ ===
    # =========================================================================
    @staticmethod
    def draw_pre_battle(screen, inventory_cards: list, battle_hand: list, floor: int, start_btn: Button):
        """Отрисовка подготовки к бою (выбор карт)"""
        screen.fill(DARK_GRAY)

        # Заголовок
        title = _ensure_fonts()['large'].render("Снаряжение в бой", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Счётчик выбранных карт
        count_text = _ensure_fonts()['medium'].render(f"Выбрано: {len(battle_hand)}/5", True, WHITE)
        screen.blit(count_text, (SCREEN_WIDTH // 2 - count_text.get_width() // 2, 75))

        # Этаж
        floor_text = _ensure_fonts()['small'].render(f"Этаж {floor}/{MAX_FLOOR}", True, LIGHT_GRAY)
        screen.blit(floor_text, (SCREEN_WIDTH // 2 - floor_text.get_width() // 2, 105))

        # Карты инвентаря (все доступны для выбора)
        for i, card in enumerate(inventory_cards):
            card.set_position(50 + (i % 8) * 140, 150 + (i // 8) * 200)
            card.draw(screen, force_available=True)
            if card.selected_for_battle:
                pygame.draw.rect(screen, GREEN,
                               (card.x - 2, card.y - 2, card.width + 4, card.height + 4), 2)

        # Кнопка "В БОЙ!"
        start_btn = Button(SCREEN_WIDTH // 2 - 100, 720, 200, 60, "В БОЙ!", RED)
        start_btn.enabled = True
        start_btn.draw(screen)

        # Подсказка
        hint = _ensure_fonts()['tiny'].render("Кликните на карты для выбора (0-5)", True, LIGHT_GRAY)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 680))

    # =========================================================================
    # === БОЙ ===
    # =========================================================================
    @staticmethod
    def draw_battle(screen, player_icon, player_health: HealthBar, gold: int,
                    dice_list: list, battle_hand: list, end_turn_btn: Button,
                    turn: str, message: str, current_enemy, enemy_health: HealthBar,
                    enemy_info_visible: bool, enemy_info_pos: tuple,
                    heal_flash: int, hero_damage_flash: int, enemy_damage_flash: int,
                    floor: int, dice_count: int, total_wins: int):
        """Отрисовка боя (полная версия)"""
        screen.fill(DARK_GRAY)

        # Заголовок этажа
        floor_text = _ensure_fonts()['medium'].render(f"Этаж {floor}/{MAX_FLOOR}", True, GOLD)
        screen.blit(floor_text, (SCREEN_WIDTH // 2 - floor_text.get_width() // 2, 10))

        # === ГЕРОЙ ===
        player_icon.draw(screen)
        player_text = _ensure_fonts()['small'].render("Герой", True, GREEN)
        screen.blit(player_text, UI_POSITIONS['hero_name'])

        # Эффект лечения
        if heal_flash > 0:
            pygame.draw.rect(screen, GREEN,
                           (player_health.x - 3, player_health.y - 3,
                            player_health.width + 6, player_health.height + 6),
                           3, border_radius=7)

        # Эффект урона по герою
        if hero_damage_flash > 0:
            hero_rect = pygame.Rect(UI_POSITIONS['hero_icon'][0] - 5,
                                  UI_POSITIONS['hero_icon'][1] - 5, 90, 90)
            pygame.draw.rect(screen, RED, hero_rect, 6, border_radius=15)

        player_health.draw(screen)

        # Золото
        IconRenderer.draw_gold_icon(screen, UI_POSITIONS['hero_gold'][0],
                                   UI_POSITIONS['hero_gold'][1], 25)
        gold_text = _ensure_fonts()['small'].render(f"{gold}", True, GOLD)
        screen.blit(gold_text, (UI_POSITIONS['hero_gold'][0] + 30, UI_POSITIONS['hero_gold'][1]))

        # Статистика
        dice_text = _ensure_fonts()['tiny'].render(
            f"Кубиков: {dice_count} | Карт: {len(battle_hand)} | Победы: {total_wins}",
            True, LIGHT_GRAY
        )
        screen.blit(dice_text, (140, 115))

        # === ПОЛЕ БОЯ ===
        GameRenderer._draw_battle_field(screen, dice_list, battle_hand)

        # === КНОПКА И ХОД ===
        end_turn_btn.draw(screen)
        turn_text = _ensure_fonts()['medium'].render(
            f"{'ВАШ ХОД' if turn == 'PLAYER' else 'ХОД ВРАГА'}",
            True, YELLOW if turn == "PLAYER" else RED
        )
        screen.blit(turn_text, UI_POSITIONS['turn_text'])

        # === ВРАГ ===
        if current_enemy:
            if enemy_damage_flash > 0:
                enemy_rect = pygame.Rect(UI_POSITIONS['enemy_icon'][0] - 5,
                                       UI_POSITIONS['enemy_icon'][1] - 5, 130, 130)
                pygame.draw.rect(screen, RED, enemy_rect, 6, border_radius=15)

            enemy_health.draw(screen)
            current_enemy.draw(screen, UI_POSITIONS['enemy_icon'][0],
                             UI_POSITIONS['enemy_icon'][1])

            if enemy_info_visible:
                GameRenderer._draw_enemy_tooltip(screen, current_enemy, enemy_info_pos)

        # === СООБЩЕНИЕ ===
        if message:
            msg_surf = _ensure_fonts()['small'].render(message, True, WHITE)
            pygame.draw.rect(screen, DARK_BLUE,
                           (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2 - 10, 730,
                            msg_surf.get_width() + 20, 35),
                           border_radius=5)
            screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 735))

    @staticmethod
    def _draw_battle_field(screen, dice_list: list, battle_hand: list):
        """Отрисовка поля боя (кубики + карты)"""
        # Зона кубиков
        pygame.draw.rect(screen, CARD_BG, pygame.Rect(*UI_POSITIONS['dice_zone']), border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, pygame.Rect(*UI_POSITIONS['dice_zone']), 2, border_radius=10)
        dice_label = _ensure_fonts()['small'].render("Кубики (клик для выбора)", True, LIGHT_GRAY)
        screen.blit(dice_label, (UI_POSITIONS['dice_zone'][0] + 10, UI_POSITIONS['dice_zone'][1] - 25))
        for dice in dice_list:
            dice.draw(screen)

        # Зона карт
        pygame.draw.rect(screen, CARD_BG, pygame.Rect(*UI_POSITIONS['card_zone']), border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, pygame.Rect(*UI_POSITIONS['card_zone']), 2, border_radius=10)
        card_label = _ensure_fonts()['small'].render("Карты (клик после кубика)", True, LIGHT_GRAY)
        screen.blit(card_label, (UI_POSITIONS['card_zone'][0] + 10, UI_POSITIONS['card_zone'][1] - 25))
        card_start_x = UI_POSITIONS['card_zone'][0] + 15
        for i, card in enumerate(battle_hand[:5]):
            card.set_position(card_start_x + i * 165, UI_POSITIONS['card_zone'][1] + 10)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(screen)

    @staticmethod
    def _draw_enemy_tooltip(screen, enemy, pos: tuple):
        """Всплывающая информация о враге"""
        info_lines = enemy.get_info_text()
        max_w = max(_ensure_fonts()['tiny'].render(l, True, WHITE).get_width() for l in info_lines)
        box_w, box_h = max_w + 20, len(info_lines) * 18 + 10
        x = min(pos[0], SCREEN_WIDTH - box_w - 10)
        y = min(pos[1], SCREEN_HEIGHT - box_h - 10)

        # Фон
        pygame.draw.rect(screen, DARK_BLUE, (x, y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, GOLD, (x, y, box_w, box_h), 2, border_radius=8)

        # Текст с цветовой кодировкой
        for i, line in enumerate(info_lines):
            if "ИММУНИТЕТ" in line:
                color = WHITE
            elif "x4" in line:
                color = PURPLE  # x4 - фиолетовый
            elif "x2" in line:
                color = GREEN  # x2 - зелёный
            elif "x1" in line and "обычный" not in line.lower():
                color = YELLOW  # x1 - жёлтый
            elif "x0.5" in line:
                color = ORANGE  # x0.5 - оранжевый
            elif "x0.25" in line:
                color = RED  # x0.25 - красный
            elif "ДУХ:" in line or "ЭЛЕМЕНТАЛЬ:" in line:
                color = GOLD
            elif "Эффективность" in line:
                color = CYAN
            elif "HP:" in line or "Урон:" in line or "Тип:" in line:
                color = CYAN
            else:
                color = WHITE

            screen.blit(_ensure_fonts()['tiny'].render(line, True, color), (x + 10, y + 5 + i * 18))

    @staticmethod
    def _draw_card_tooltip(screen, card, pos: tuple):
        """Всплывающая подсказка о карте (как в бою)"""
        # Определение типа эффекта для отображения
        effect_desc = card.description
        if card.effect_type == "damage":
            effect_desc = f"Урон = кубик + {card.effect_value}"
        elif card.effect_type == "block":
            effect_desc = f"Блок = {card.effect_value}"
        elif card.effect_type == "heal":
            effect_desc = f"Лечение = {card.effect_value}"
        elif card.effect_type == "vampirism":
            effect_desc = f"Вампиризм: урон + {card.effect_value}, лечение"
        elif card.effect_type == "special":
            effect_desc = f"Урон + блок/лечение"

        # Требование кубиков
        req_text = "Любой" if card.dice_requirement == "any" else \
                   "Чётные" if card.dice_requirement == "even" else \
                   "Нечётные" if card.dice_requirement == "odd" else \
                   str(card.dice_requirement)

        lines = [
            f"{card.name}",
            f"Разряд: {card.tier} | Стихия: {card.damage_type}",
            f"Кубиков: {card.dice_cost} | Требование: {req_text}",
            f"Эффект: {effect_desc}",
            f"Цена: {card.price}G",
        ]

        max_w = max(_ensure_fonts()['tiny'].render(l, True, WHITE).get_width() for l in lines)
        box_w, box_h = max_w + 20, len(lines) * 18 + 10
        x = min(pos[0], SCREEN_WIDTH - box_w - 10)
        y = min(pos[1], SCREEN_HEIGHT - box_h - 10)

        pygame.draw.rect(screen, DARK_BLUE, (x, y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, GOLD, (x, y, box_w, box_h), 2, border_radius=8)

        for i, line in enumerate(lines):
            screen.blit(_ensure_fonts()['tiny'].render(line, True, WHITE), (x + 10, y + 5 + i * 18))

    @staticmethod
    def _draw_armor_tooltip(screen, armor, pos: tuple):
        """Всплывающая подсказка о броне"""
        lines = [
            f"{armor.name}",
            f"Разряд: {armor.tier} | Защита: {armor.defense}",
            f"Тип: {armor.armor_type}",
            armor.get_effect_text(),
        ]

        max_w = max(_ensure_fonts()['tiny'].render(l, True, WHITE).get_width() for l in lines)
        box_w, box_h = max_w + 20, len(lines) * 18 + 10
        x = min(pos[0], SCREEN_WIDTH - box_w - 10)
        y = min(pos[1], SCREEN_HEIGHT - box_h - 10)

        pygame.draw.rect(screen, DARK_BLUE, (x, y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, BLUE, (x, y, box_w, box_h), 2, border_radius=8)

        for i, line in enumerate(lines):
            color = GOLD if i == 0 else WHITE
            screen.blit(_ensure_fonts()['tiny'].render(line, True, color), (x + 10, y + 5 + i * 18))

    # =========================================================================
    # === НАГРАДА ===
    # =========================================================================
    @staticmethod
    def draw_reward_screen(screen, reward_cards: list, floor: int,
                          dice_count: int, inventory_size: int, total_wins: int):
        """Отрисовка экрана выбора награды"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок
        title = _ensure_fonts()['large'].render("ВЫБЕРИТЕ НАГРАДУ!", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Этаж
        floor_text = _ensure_fonts()['medium'].render(f"Этаж {floor} завершён", True, GREEN)
        screen.blit(floor_text, (SCREEN_WIDTH // 2 - floor_text.get_width() // 2, 140))

        # Карты наград
        for i, card in enumerate(reward_cards):
            card.set_position(180 + i * 270, 280)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(screen)

        # Статистика
        info_text = _ensure_fonts()['small'].render(
            f"Кубиков: {dice_count} | Карт: {inventory_size} | Победы: {total_wins}",
            True, LIGHT_GRAY
        )
        screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, 520))

        # Подсказка
        hint = _ensure_fonts()['tiny'].render("Кликните на карту чтобы добавить в инвентарь", True, CYAN)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 560))

    # =========================================================================
    # === МАГАЗИН ===
    # =========================================================================
    @staticmethod
    def draw_shop(screen, shop_cards: list, inventory_cards: list, gold: int,
                 selected_upgrade_card: int, upgrade_flash: int,
                 shop_buttons: dict, message: str = ""):
        """Отрисовка магазина"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок (центрируем)
        title = _ensure_fonts()['large'].render("МАГАЗИН", True, GOLD)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 80))

        # Золото
        IconRenderer.draw_gold_icon(screen, SCREEN_WIDTH // 2 - 15, 130, 25)
        gold_text = _ensure_fonts()['medium'].render(f"{gold}", True, GOLD)
        screen.blit(gold_text, (SCREEN_WIDTH // 2 + 20, 130))

        # Карты на продажу
        buy_title = _ensure_fonts()['small'].render("Купить карты:", True, WHITE)
        screen.blit(buy_title, (150, 170))
        for i, card in enumerate(shop_cards):
            card.set_position(150 + i * 200, 210)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(screen, show_price=True, price_type="buy", player_gold=gold)

        # Инвентарь (продажа/апгрейд)
        sell_title = _ensure_fonts()['small'].render("Инвентарь (двойной клик для продажи):", True, WHITE)
        screen.blit(sell_title, (150, 420))
        start_x, start_y = 150, 460
        cards_per_row = 6
        for i, card in enumerate(inventory_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            card.set_position(start_x + col * 155, start_y + row * 200)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(screen, show_price=True, price_type="sell", player_gold=gold)
            if selected_upgrade_card == i:
                pygame.draw.rect(screen, BLUE,
                               (card.x - 3, card.y - 3, card.width + 6, card.height + 6),
                               3, border_radius=12)

        # Эффект апгрейда
        if upgrade_flash > 0:
            pygame.draw.rect(screen, GOLD,
                           (150 - 5, 460 - 5, 6 * 155 + 10,
                            max(200, (len(inventory_cards) // 6 + 1) * 200 + 10)),
                           4, border_radius=15)

        # Информация об апгрейде
        if selected_upgrade_card is not None and 0 <= selected_upgrade_card < len(inventory_cards):
            card = inventory_cards[selected_upgrade_card]
            upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
            upgrade_color = GREEN if gold >= upgrade_cost else RED
            upgrade_key = (card.name, card.tier)

            if upgrade_key in CARD_UPGRADES:
                upgrade_name = CARD_UPGRADES[upgrade_key][0]
                upgrade_info = _ensure_fonts()['small'].render(f"→ {upgrade_name} за", True, WHITE)
            else:
                upgrade_info = _ensure_fonts()['small'].render(f"Апгрейд T{card.tier + 1}:", True, WHITE)

            cost_info = _ensure_fonts()['small'].render(f"{upgrade_cost}G", True, upgrade_color)
            screen.blit(upgrade_info, (450, 670))
            screen.blit(cost_info, (650, 670))
            IconRenderer.draw_gold_icon(screen, 710, 668, 18)

        # Кнопки
        if shop_buttons.get('next_floor'):
            shop_buttons['next_floor'].draw(screen)
        if selected_upgrade_card is not None:
            if shop_buttons.get('upgrade'):
                shop_buttons['upgrade'].draw(screen)
            if shop_buttons.get('cancel'):
                shop_buttons['cancel'].draw(screen)

        # Сообщение
        if message:
            msg = _ensure_fonts()['small'].render(message, True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 780))

    # =========================================================================
    # === СНАРЯЖЕНИЕ ===
    # =========================================================================
    @staticmethod
    def draw_treasure(screen, treasure_items: list):
        """Отрисовка сокровищницы"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок (с центрированием)
        title = _ensure_fonts()['large'].render("Снаряжение", True, GOLD)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 50))

        # Предметы - по центру с учётом количества
        item_count = len(treasure_items)
        item_width = 150
        total_width = item_count * item_width
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, item in enumerate(treasure_items):
            x = start_x + i * item_width
            if item["type"] == "card":
                from modules.cards import AbilityCard
                card = AbilityCard(*item["data"])
                card.set_position(x, 150)
                card.draw(screen, force_available=True)
            elif item["type"] == "armor":
                from modules.entities import Armor
                d = item["data"]
                tier = d.get("tier", 1)
                armor = Armor(d["name"], tier, d["defense"], d.get("type", "normal"), d.get("asset"))
                armor.draw(screen, x, 150)
                # Подсветка при наведении
                armor_rect = pygame.Rect(x, 150, 50, 50)
                if armor_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, WHITE, armor_rect, 2)

        # Подсказка
        msg = _ensure_fonts()['small'].render("Кликните чтобы забрать", True, WHITE)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 500))

    # =========================================================================
    # === КОСТЁР ===
    # =========================================================================
    @staticmethod
    def draw_campfire(screen, message: str = ""):
        """Отрисовка костра (лечение)"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок (центрируем)
        title = _ensure_fonts()['large'].render("Костёр", True, GOLD)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 200))

        # Иконка костра
        pygame.draw.circle(screen, ORANGE, (SCREEN_WIDTH // 2, 300), 40)
        pygame.draw.circle(screen, RED, (SCREEN_WIDTH // 2, 300), 30)
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH // 2, 300), 20)

        # Сообщение
        msg = _ensure_fonts()['medium'].render(message or "HP полностью восстановлено! Макс HP +10", True, GREEN)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 380))

        # Кнопка
        btn = Button(SCREEN_WIDTH // 2 - 100, 450, 200, 60, "Дальше", GREEN)
        btn.draw(screen)

    # =========================================================================
    # === ВЫБОР СОБЫТИЯ ===
    # =========================================================================
    @staticmethod
    def draw_event_choice(screen, event_choices: list):
        """Отрисовка выбора следующего события"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Заголовок (с центрированием)
        title = _ensure_fonts()['large'].render("Выберите следующее событие", True, GOLD)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 100))

        # Карточки событий (центрируем по количеству)
        card_width = 220
        card_count = len(event_choices)
        total_width = card_count * card_width
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, event in enumerate(event_choices):
            x = start_x + i * card_width
            rect = pygame.Rect(x, 250, card_width, 200)

            # Фон карточки
            pygame.draw.rect(screen, CARD_BG, rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, rect, 3, border_radius=10)

            # Иконка (центрирована, если есть)
            if event.get("icon"):
                icon = _ensure_fonts()['large'].render(event["icon"], True, WHITE)
                icon_x = x + (card_width - icon.get_width()) // 2
                screen.blit(icon, (icon_x, 270))

            # Название (центрировано и с переносом если нужно)
            name_text = event["name"]
            name = _ensure_fonts()['medium'].render(name_text, True, WHITE)
            name_x = x + (card_width - name.get_width()) // 2
            screen.blit(name, (name_x, 350))

            # Подсказка при наведении
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, WHITE, rect, 5, border_radius=10)

    # =========================================================================
    # === GAME OVER ===
    # =========================================================================
    @staticmethod
    def draw_game_over(screen, floor: int, total_wins: int, next_floor_btn: Button):
        """Отрисовка экрана поражения"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Заголовок (центрируем)
        text = _ensure_fonts()['large'].render("ПОРАЖЕНИЕ", True, RED)
        text_x = (SCREEN_WIDTH - text.get_width()) // 2
        screen.blit(text, (text_x, 300))

        # Информация
        info = _ensure_fonts()['medium'].render(f"Этаж: {floor} | Победы: {total_wins}", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 360))

        # Кнопка
        next_floor_btn.draw(screen)

    # =========================================================================
    # === ПОБЕДА ===
    # =========================================================================
    @staticmethod
    def draw_victory(screen, total_wins: int, next_floor_btn: Button):
        """Отрисовка экрана победы"""
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Заголовок (центрируем)
        text = _ensure_fonts()['large'].render("ПОБЕДА!", True, GOLD)
        text_x = (SCREEN_WIDTH - text.get_width()) // 2
        screen.blit(text, (text_x, 300))

        # Информация (центрируем)
        info = _ensure_fonts()['medium'].render(f"Всего побед: {total_wins}", True, WHITE)
        info_x = (SCREEN_WIDTH - info.get_width()) // 2
        screen.blit(info, (info_x, 360))

        # Конфетти (упрощённо)
        import random
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = [GOLD, RED, GREEN, BLUE, PURPLE][random.randint(0, 4)]
            pygame.draw.circle(screen, color, (x, y), 3)

        # Кнопка
        next_floor_btn.draw(screen)

    # =========================================================================
    # === УНИВЕРСАЛЬНЫЙ МЕТОД ОТРИСОВКИ ===
    # =========================================================================
    @staticmethod
    def draw(screen, game_state: str, **kwargs):
        """
        Универсальный метод отрисовки по состоянию игры

        Пример использования:
        GameRenderer.draw(screen, "BATTLE",
                         player_icon=icon, player_health=health, ...)
        """
        draw_methods = {
            "MENU": lambda: GameRenderer.draw_menu(screen, kwargs.get('start_btn')),
            "MAP": lambda: GameRenderer.draw_map(screen,
                        kwargs.get('nodes', []), kwargs.get('floor', 1),
                        kwargs.get('player_hp', 25), kwargs.get('max_hp', 25),
                        kwargs.get('gold', 0), kwargs.get('inventory_btn'),
                        kwargs.get('message', "")),
            "INVENTORY": lambda: GameRenderer.draw_inventory(screen,
                        kwargs.get('inventory_cards', []), kwargs.get('inventory_armor', []),
                        kwargs.get('equipped_armor'), kwargs.get('map_btn'),
                        kwargs.get('message', ""),
                        kwargs.get('armor_tooltip_visible', False),
                        kwargs.get('armor_tooltip_pos', (0, 0)),
                        kwargs.get('armor_tooltip_armor', None),
                        kwargs.get('inventory_tab', 'cards'),
                        kwargs.get('inventory_scroll', 0)),
            "PRE_BATTLE": lambda: GameRenderer.draw_pre_battle(screen,
                        kwargs.get('inventory_cards', []), kwargs.get('battle_hand', []),
                        kwargs.get('floor', 1)),
            "BATTLE": lambda: GameRenderer.draw_battle(screen,
                        kwargs.get('player_icon'), kwargs.get('player_health'),
                        kwargs.get('gold', 0), kwargs.get('dice_list', []),
                        kwargs.get('battle_hand', []), kwargs.get('end_turn_btn'),
                        kwargs.get('turn', "PLAYER"), kwargs.get('message', ""),
                        kwargs.get('current_enemy'), kwargs.get('enemy_health'),
                        kwargs.get('enemy_info_visible', False),
                        kwargs.get('enemy_info_pos', (0, 0)),
                        kwargs.get('heal_flash', 0), kwargs.get('hero_damage_flash', 0),
                        kwargs.get('enemy_damage_flash', 0), kwargs.get('floor', 1),
                        kwargs.get('dice_count', 3), kwargs.get('total_wins', 0)),
            "REWARD": lambda: GameRenderer.draw_reward_screen(screen,
                        kwargs.get('reward_cards', []), kwargs.get('floor', 1),
                        kwargs.get('dice_count', 3), kwargs.get('inventory_size', 0),
                        kwargs.get('total_wins', 0)),
            "SHOP": lambda: GameRenderer.draw_shop(screen,
                        kwargs.get('shop_cards', []), kwargs.get('inventory_cards', []),
                        kwargs.get('gold', 0), kwargs.get('selected_upgrade_card'),
                        kwargs.get('upgrade_flash', 0), kwargs.get('shop_buttons', {}),
                        kwargs.get('message', "")),
            "TREASURE": lambda: GameRenderer.draw_treasure(screen,
                        kwargs.get('treasure_items', [])),
            "CAMPFIRE": lambda: GameRenderer.draw_campfire(screen,
                        kwargs.get('message', "")),
            "EVENT_CHOICE": lambda: GameRenderer.draw_event_choice(screen,
                        kwargs.get('event_choices', [])),
            "GAME_OVER": lambda: GameRenderer.draw_game_over(screen,
                        kwargs.get('floor', 1), kwargs.get('total_wins', 0),
                        kwargs.get('next_floor_btn')),
            "VICTORY": lambda: GameRenderer.draw_victory(screen,
                        kwargs.get('total_wins', 0), kwargs.get('next_floor_btn')),
        }

        draw_func = draw_methods.get(game_state)
        if draw_func:
            draw_func()