"""Главный класс игры — оркестрация"""
import pygame
import sys
from modules.config import *
import modules.utils.fonts as fonts_module
from modules.utils import IconRenderer
from modules.cards.card import _ensure_fonts
from modules.entities import Dice, Enemy, CharacterIcon, Armor
from modules.ui.components import HealthBar, Button
from modules.cards import AbilityCard
from modules.ui import GameRenderer
from modules.core import validate_game_data, save_game, load_game, SoundManager, ParticleSystem
from modules.systems import BattleManager, MapManager, InventoryManager, EventManager, TurnManager


class Game:
    def __init__(self):
        pygame.init()  # ← Инициализируем pygame

        # ✅ Инициализируем шрифты ПОСЛЕ pygame.init()
        from modules.utils import get_fonts
        fonts_module.FONTS = get_fonts()  # Заполняем глобальный кэш

        # Локальная ссылка для удобства
        FONTS = get_fonts()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dicey Dungeons - Map Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # Менеджеры
        self.map_mgr = MapManager()
        self.inv_mgr = InventoryManager()
        self.inv_mgr.gold = STARTING_GOLD  # Стартовое золото
        self.event_mgr = EventManager()
        self.turn_mgr = TurnManager()
        self.particles = ParticleSystem()
        SoundManager.init()

        # Состояние
        self.floor = 1
        self.game_state = "MENU"
        self.message, self.message_timer = "", 0
        self._init_ui()

    def _init_ui(self):
        """Инициализация UI"""
        self.player_health = HealthBar(UI_POSITIONS['hero_hp'][0], UI_POSITIONS['hero_hp'][1],
                                       200, 30, PLAYER_MAX_HP, GREEN)
        self.start_btn = Button(UI_POSITIONS['start_btn_center'] - 100, 380, 200, 60, "Начать игру", GREEN)
        self.fight_btn = Button(SCREEN_WIDTH // 2 - 100, 720, 200, 60, "В БОЙ!", RED)
        self.end_turn_btn = Button(*UI_POSITIONS['end_turn_btn'], "Завершить ход", BLUE)
        self.inventory_btn = Button(1000, 10, 180, 60, "Инвентарь", BLUE, icon_image_path="assets/images/icon_inventory.png")
        self.player_icon = CharacterIcon(*UI_POSITIONS['hero_icon'], 80, "assets/images/hero.png", "hero")
        self.map_btn = Button(1050, 20, 130, 40, "Карта", BLUE)
        self.to_map_btn = Button(SCREEN_WIDTH // 2 - 80, 700, 160, 50, "На карту", BLUE)
        self.fight_from_map_btn = Button(SCREEN_WIDTH // 2 - 100, 640, 200, 50, "В БОЙ!", RED)
        self.next_floor_btn = Button(SCREEN_WIDTH // 2 - 80, 500, 160, 50, "В меню", BLUE)
        self.turn = "PLAYER"
        self.enemy_info_visible = False
        self.enemy_info_pos = (0, 0)
        self.card_tooltip_visible = False
        self.card_tooltip_pos = (0, 0)
        self.card_tooltip_card = None
        self.armor_tooltip_visible = False
        self.armor_tooltip_pos = (0, 0)
        self.armor_tooltip_armor = None
        self.player_block = 0  # Блок игрока
        self.inventory_tab = "cards"  # "cards" или "armor"
        self.inventory_scroll = 0  # Позиция скролла
        self.dragging_scroll = False  # Флаг для перетаскивания ползунка
        self.event_choices = []
        self.selected_upgrade_card = None
        self.upgrade_flash_timer = 0
        self.shop_buttons = {}
        self.treasure_items = []
        self.heal_flash_timer = 0
        self.hero_damage_flash_timer = 0
        self.enemy_damage_flash_timer = 0
        # Тестовая кнопка убийства врага
        self.kill_enemy_btn = Button(SCREEN_WIDTH - 150, 650, 130, 40, "[TEST] Убить", RED)
        # Тестовая кнопка выбора врага
        self.test_enemy_btn = Button(SCREEN_WIDTH - 150, 600, 130, 40, "[TEST] Враг", BLUE)
        self.test_enemy_menu_visible = False
        self.test_enemies = []  # Список всех врагов для тестирования
        self.test_enemy_scroll = 0  # Скролл в меню выбора врага
        # Атрибуты для MENU
        self.max_floor = MAX_FLOOR
        self.gold = 0
        self.total_wins = 0
        self.map_nodes = []
        self.player_hp = PLAYER_MAX_HP
        self.player_max_hp = PLAYER_MAX_HP
        self.dice_count = DICE_COUNT
        self.dice_list = []
        self.battle_hand = []
        self.current_enemy = None
        self.enemy_health = None
        self.inventory_cards = []
        self.inventory_armor = []
        self.equipped_armor = None
        self.next_enemy = None  # Следующий враг для отображения на карте
        self.message = ""
        self.message_timer = 0

    def _reset_game(self):
        """Сброс игры"""
        self.floor = 1
        self.max_floor = MAX_FLOOR
        self.gold = self.inv_mgr.gold
        self.player_hp = self.player_max_hp = PLAYER_MAX_HP
        self.player_block = 0
        self.dice_count = DICE_COUNT
        self.total_wins = 0
        self.dice_list = []
        self.battle_hand = []
        self.current_enemy = None
        self.enemy_health = None
        self.inventory_cards = self.inv_mgr.cards
        self.inventory_armor = self.inv_mgr.armor
        self.equipped_armor = self.inv_mgr.equipped_armor
        self.map_nodes = self.map_mgr.nodes
        self.map_btn = Button(1050, 20, 130, 40, "Карта", BLUE)
        self.to_map_btn = Button(SCREEN_WIDTH // 2 - 80, 700, 160, 50, "На карту", BLUE)
        self.turn = "PLAYER"
        self.enemy_info_visible = False
        self.enemy_info_pos = (0, 0)
        self.heal_flash_timer = 0
        self.hero_damage_flash_timer = 0
        self.enemy_damage_flash_timer = 0
        self.inv_mgr.gold = STARTING_GOLD
        self.player_hp = self.player_max_hp = PLAYER_MAX_HP
        self.player_block = 0
        self.dice_count = DICE_COUNT
        self.inv_mgr.cards = [AbilityCard(*c) for c in STARTING_INVENTORY]
        self.inv_mgr.armor = [Armor("Старые доспехи", 0, 0, asset_path="armor_metal_0.png")]
        self.inv_mgr.equipped_armor = self.inv_mgr.armor[0]
        self.map_mgr.reset()  # Сброс карты
        self.map_mgr.generate(1)  # Генерация новой карты
        self.next_enemy = self._create_enemy(1)  # Создаём первого врага
        self._init_test_enemies()  # Инициализация тестовых врагов
        self.game_state = "MAP"

    def run(self):
        """Главный цикл"""
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEWHEEL:
                if self.game_state == "INVENTORY":
                    max_scroll = 0
                    if self.inventory_tab == "cards":
                        max_scroll = max(0, len(self.inventory_cards) - 10)
                    else:
                        max_scroll = max(0, len(self.inventory_armor) - 16)
                    self.inventory_scroll = max(0, min(self.inventory_scroll - event.y, max_scroll))
                elif self.game_state == "MAP" and self.test_enemy_menu_visible:
                    max_scroll = max(0, len(self.test_enemies) - 8)
                    self.test_enemy_scroll = max(0, min(self.test_enemy_scroll - event.y, max_scroll))
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "MAP" and self.test_enemy_menu_visible:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        max_scroll = max(0, len(self.test_enemies) - 8)
                        self.test_enemy_scroll = min(self.test_enemy_scroll + 1, max_scroll)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.test_enemy_scroll = max(0, self.test_enemy_scroll - 1)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_scroll:
                    self.dragging_scroll = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_scroll and self.game_state == "INVENTORY":
                    # Перетаскивание ползунка
                    pos = pygame.mouse.get_pos()
                    scroll_bar_x = SCREEN_WIDTH - 30
                    scroll_bar_y = 180
                    if self.inventory_tab == "cards":
                        scroll_bar_height = 150
                        max_items = len(self.inventory_cards)
                        visible = 10
                    else:
                        scroll_bar_height = 320
                        max_items = len(self.inventory_armor)
                        visible = 16
                    
                    if max_items > visible:
                        max_scroll = max_items - visible
                        relative_y = (pos[1] - scroll_bar_y) / scroll_bar_height
                        self.inventory_scroll = int(relative_y * max_scroll)
                        self.inventory_scroll = max(0, min(self.inventory_scroll, max_scroll))
            elif event.type == pygame.USEREVENT:
                self.turn_mgr.on_enemy_turn_event(self._enemy_turn)

    def _handle_click(self, pos):
        """Обработка кликов по состоянию"""
        if self.game_state == "MENU" and self.start_btn.is_clicked(pos):
            self._reset_game()
        elif self.game_state == "GAME_OVER" and self.next_floor_btn.is_clicked(pos):
            self.game_state = "MENU"
        elif self.game_state == "VICTORY" and self.next_floor_btn.is_clicked(pos):
            self.game_state = "MENU"
        elif self.game_state == "MAP":
            if self.inventory_btn.is_clicked(pos):
                self.game_state = "INVENTORY"
            elif hasattr(self, 'fight_from_map_btn') and self.fight_from_map_btn.is_clicked(pos):
                # Клик по кнопке "В бой" - переход к выбору карт
                self._visit_location(self.map_mgr.node.type)
            elif self.test_enemy_btn.is_clicked(pos):
                self.test_enemy_menu_visible = not self.test_enemy_menu_visible
                self.test_enemy_scroll = 0
            # Обработка выбора врага из тестового меню
            elif self.test_enemy_menu_visible:
                menu_x, menu_y = SCREEN_WIDTH - 290, 540
                menu_w, item_h = 270, 35
                visible_count = 8  # Сколько врагов видно
                max_scroll = max(0, len(self.test_enemies) - visible_count)
                for i in range(self.test_enemy_scroll, min(self.test_enemy_scroll + visible_count, len(self.test_enemies))):
                    enemy = self.test_enemies[i]
                    btn_rect = pygame.Rect(menu_x, menu_y + (i - self.test_enemy_scroll) * item_h, menu_w, item_h)
                    if btn_rect.collidepoint(pos):
                        # Создаём врага для боя
                        self.next_enemy = Enemy(
                            name=enemy["name"],
                            hp=enemy["hp"],
                            damage_range=enemy["dmg"],
                            image_path=f"assets/images/{enemy['icon']}.png",
                            icon_type=enemy["icon"],
                            enemy_type=enemy["enemy_type"],
                            damage_type=enemy["dmg_type"]
                        )
                        self.test_enemy_menu_visible = False
                        break
                # Закрыть меню если клик вне его
                menu_rect = pygame.Rect(menu_x, menu_y, 270, visible_count * item_h + 10)
                if not menu_rect.collidepoint(pos) and not self.test_enemy_btn.is_clicked(pos):
                    self.test_enemy_menu_visible = False
        elif self.game_state == "PRE_BATTLE":
            if self.fight_btn.is_clicked(pos):
                # Выбрать только отмеченные карты (до 5)
                self.inv_mgr.selected_cards = [c for c in self.inventory_cards if c.selected_for_battle][:5]
                self._start_battle()
            else:
                # Клик по карте - переключить выбор
                for card in self.inventory_cards:
                    if card.is_clicked(pos):
                        card.selected_for_battle = not card.selected_for_battle
                        break
        elif self.game_state == "INVENTORY":
            if self.map_btn.is_clicked(pos):
                self.game_state = "MAP"
                self.card_tooltip_visible = False
                self.armor_tooltip_visible = False
            # Клик по вкладкам
            cards_tab_rect = pygame.Rect(50, 120, 150, 40)
            armor_tab_rect = pygame.Rect(210, 120, 150, 40)
            if cards_tab_rect.collidepoint(pos):
                self.inventory_tab = "cards"
                self.inventory_scroll = 0
                return
            if armor_tab_rect.collidepoint(pos):
                self.inventory_tab = "armor"
                self.inventory_scroll = 0
                return
            # Клик по ползунку скролла
            scroll_bar_x = SCREEN_WIDTH - 30
            scroll_bar_y = 180
            if self.inventory_tab == "cards":
                scroll_bar_height = 150
                max_items = len(self.inventory_cards)
                visible = 10
            else:
                scroll_bar_height = 420
                max_items = len(self.inventory_armor)
                visible = 12
            
            if max_items > visible:
                scroll_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, 15, scroll_bar_height)
                if scroll_rect.collidepoint(pos):
                    # Вычисляем позицию скролла по клику
                    max_scroll = max_items - visible
                    relative_y = (pos[1] - scroll_bar_y) / scroll_bar_height
                    self.inventory_scroll = int(relative_y * max_scroll)
                    self.inventory_scroll = max(0, min(self.inventory_scroll, max_scroll))
                    self.dragging_scroll = True
                    return
            # Клик по броне - выбор или описание (с учётом скролла и большего размера)
            if self.inventory_tab == "armor":
                armor_cols = 6
                armor_start = self.inventory_scroll
                armor_visible = self.inventory_armor[armor_start:armor_start + 12]
                for i, armor in enumerate(armor_visible):
                    row = i // armor_cols
                    col = i % armor_cols
                    x = 50 + col * 140
                    y = 180 + row * 140
                    if armor.is_clicked(pos, x, y):
                        actual_index = armor_start + i
                        armor = self.inventory_armor[actual_index]
                        if self.equipped_armor == armor:
                            self.armor_tooltip_visible = not self.armor_tooltip_visible
                            self.armor_tooltip_pos = pos
                            self.armor_tooltip_armor = armor
                        else:
                            self.inv_mgr.equip_armor(armor)
                            self.equipped_armor = armor
                            self.message = f"Надето: {armor.name}!"
                            self.message_timer = 60
                        return
        elif self.game_state == "SHOP":
            # Обработка кликов в магазине
            # Кнопка "На карту"
            if self.to_map_btn.is_clicked(pos) or (self.shop_buttons.get('next_floor') and self.shop_buttons['next_floor'].is_clicked(pos)):
                self.map_mgr.generate(self.floor)
                self.map_nodes = self.map_mgr.nodes
                self.next_enemy = self._create_enemy(self.floor)
                self.game_state = "MAP"
            # Кнопки улучшения/отмены
            if self.selected_upgrade_card is not None:
                if self.shop_buttons.get('upgrade') and self.shop_buttons['upgrade'].is_clicked(pos):
                    success, msg = self.inv_mgr.upgrade_card(self.selected_upgrade_card)
                    self.message = msg
                    self.message_timer = 60
                    if success:
                        self.upgrade_flash_timer = 15
                        self.inventory_cards = self.inv_mgr.cards
                    self.selected_upgrade_card = None
                    return
                if self.shop_buttons.get('cancel') and self.shop_buttons['cancel'].is_clicked(pos):
                    self.selected_upgrade_card = None
                    return
            # Клик по карте в магазине - покупка
            for i, card in enumerate(self.shop_cards):
                if card.is_clicked(pos):
                    if self.inv_mgr.gold >= card.price:
                        self.inv_mgr.gold -= card.price
                        self.inv_mgr.cards.append(card)
                        self.inventory_cards = self.inv_mgr.cards
                        self.shop_cards.remove(card)  # Удаляем купленную карту из магазина
                        self.message = f"Куплено: {card.name}!"
                        self.message_timer = 60
                    else:
                        self.message = "Недостаточно золота!"
                        self.message_timer = 60
                    return
            # Клик по карте в инвентаре - выбор для апгрейда / продажа по двойному клику
            for i, card in enumerate(self.inventory_cards):
                if card.is_clicked(pos):
                    if hasattr(card, 'last_click_time') and pygame.time.get_ticks() - card.last_click_time < 300:
                        # Двойной клик - продажа
                        price = card.get_sell_price()
                        if price > 0:
                            self.inv_mgr.gold += price
                            self.inv_mgr.cards.pop(i)
                            self.inventory_cards = self.inv_mgr.cards
                            self.message = f"Продано: {card.name} за {price}G!"
                            self.message_timer = 60
                        card.last_click_time = 0
                    else:
                        # Первый клик - выбор для апгрейда
                        self.selected_upgrade_card = i
                        card.last_click_time = pygame.time.get_ticks()
                    return
            # Кнопка улучшения
            if self.selected_upgrade_card is not None and self.shop_buttons.get('upgrade'):
                if self.shop_buttons['upgrade'].is_clicked(pos):
                    success, msg = self.inv_mgr.upgrade_card(self.selected_upgrade_card)
                    self.message = msg
                    self.message_timer = 60
                    if success:
                        self.upgrade_flash_timer = 15
                        self.inventory_cards = self.inv_mgr.cards
                    self.selected_upgrade_card = None
                    return
            # Кнопка отмены
            if self.shop_buttons.get('cancel') and self.shop_buttons['cancel'].is_clicked(pos):
                self.selected_upgrade_card = None
                return
        elif self.game_state == "CAMPFIRE":
            # Клик по кнопке "Дальше" (координаты как в рендере)
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 60)
            if btn_rect.collidepoint(pos):
                self.map_mgr.generate(self.floor)
                self.map_nodes = self.map_mgr.nodes
                self.next_enemy = self._create_enemy(self.floor)
                self.game_state = "MAP"
        elif self.game_state in ("TREASURE",) and self.to_map_btn.is_clicked(pos):
            self.map_mgr.generate(self.floor)
            self.map_nodes = self.map_mgr.nodes
            self.next_enemy = self._create_enemy(self.floor)
            self.game_state = "MAP"
        elif self.game_state == "TREASURE":
            # Клик по предмету - забрать (центрирование как в рендере)
            item_count = len(self.treasure_items)
            item_width = 200  # Больше для крупной брони
            total_width = item_count * item_width
            start_x = (SCREEN_WIDTH - total_width) // 2
            for i, item in enumerate(self.treasure_items):
                x = start_x + i * item_width
                if item["type"] == "card":
                    item_rect = pygame.Rect(x, 150, 150, 200)
                else:
                    item_rect = pygame.Rect(x, 120, 200, 200)  # Больше для брони
                if item_rect.collidepoint(pos):
                    if item["type"] == "card":
                        from modules.cards import AbilityCard
                        card = AbilityCard(*item["data"])
                        self.inv_mgr.cards.append(card)
                        self.message = f"Получено: {card.name}!"
                    elif item["type"] == "armor":
                        from modules.entities import Armor
                        d = item["data"]
                        armor = Armor(d["name"], d.get("tier", 1), d["defense"], d.get("type", "normal"), d.get("asset"), d.get("element"))
                        self.inv_mgr.armor.append(armor)
                        self.message = f"Получено: {armor.name}!"
                    self.message_timer = 60
                    self.treasure_items = []  # Очистить после получения
                    # Переход на карту
                    self.map_mgr.generate(self.floor)
                    self.map_nodes = self.map_mgr.nodes
                    self.game_state = "MAP"
                    return
        elif self.game_state == "REWARD":
            for i, card in enumerate(self.reward_cards):
                if card.is_clicked(pos):
                    self.inv_mgr.cards.append(card)
                    self.message = f"Получена карта: {card.name}!"
                    self.message_timer = 60
                    self.card_tooltip_visible = False
                    self.card_tooltip_card = None
                    
                    # После босса - переход к следующему бою
                    self.floor += 1
                    if self.floor > MAX_FLOOR:
                        self.game_state = "VICTORY"
                    else:
                        self.map_mgr.proceed()
                        self.map_mgr.generate(self.floor)
                        self.next_enemy = self._create_enemy(self.floor)  # Новый враг для следующего этажа
                        self.game_state = "MAP"
                    break
        elif self.game_state == "BATTLE":
            # [TEST] Кнопка убийства врага
            if self.kill_enemy_btn.is_clicked(pos):
                if self.current_enemy and not self.current_enemy.dead:
                    self.current_enemy.hp = 0
                    self.current_enemy.dead = True
                    self.enemy_damage_flash_timer = 15
                    self.message = "[TEST] Враг убит!"
                    self.message_timer = 60
                    self._enemy_defeated()
                return
            # Клик на врага для показа информации
            if self.current_enemy:
                enemy_rect = pygame.Rect(UI_POSITIONS['enemy_icon'][0], UI_POSITIONS['enemy_icon'][1], 120, 120)
                if enemy_rect.collidepoint(pos):
                    self.enemy_info_visible = not self.enemy_info_visible
                    self.enemy_info_pos = pos
                    return
            # Обработка боевых кликов
            if self.turn_mgr.is_player_turn():
                self._handle_battle_click(pos)
        elif self.game_state == "EVENT_CHOICE":
            # Центрирование как в рендере
            card_width = 220
            card_count = len(self.event_choices)
            total_width = card_count * card_width
            start_x = (SCREEN_WIDTH - total_width) // 2
            for i, event in enumerate(self.event_choices):
                x = start_x + i * card_width
                rect = pygame.Rect(x, 250, card_width, 200)
                if rect.collidepoint(pos):
                    if event["type"] == "shop":
                        self.shop_cards = self.event_mgr.generate_shop_cards()
                        self._init_shop_state()
                        self.game_state = "SHOP"
                    elif event["type"] == "treasure":
                        self.treasure_items = self.event_mgr.generate_treasure()
                        self.game_state = "TREASURE"
                    elif event["type"] == "campfire":
                        self.player_max_hp += 10
                        self.player_hp = self.player_max_hp  # Полное восстановление
                        self.message = "HP полностью восстановлено! Макс HP +10"
                        self.message_timer = 120
                        self.game_state = "CAMPFIRE"
                    # После посещения - переход к следующему бою
                    self.floor += 1
                    if self.floor > MAX_FLOOR:
                        self.game_state = "VICTORY"
                    else:
                        self.map_mgr.proceed()
                        self.map_mgr.generate(self.floor)
                        self.next_enemy = self._create_enemy(self.floor)  # Новый враг для следующего этажа
                    break

    def _handle_battle_click(self, pos):
        """Обработка кликов в бою"""
        # Кубики
        for dice in self.dice_list:
            if dice.is_clicked(pos) and not dice.used:
                dice.selected = not dice.selected
                return
        # Карты
        for card in self.battle_hand:
            if card.is_clicked(pos) and any(d.selected for d in self.dice_list):
                self._assign_dice_to_card(card)
                return
        # Кнопка завершения хода
        if self.end_turn_btn.is_clicked(pos):
            self.turn = "ENEMY"
            self.turn_mgr.start_enemy_turn(self._enemy_turn)

    def _assign_dice_to_card(self, card):
        """Назначение кубиков карте"""
        selected = [d for d in self.dice_list if d.selected and not d.used]
        if len(selected) != card.dice_cost:
            self.message = f"Нужно {card.dice_cost} кубика!"
            self.message_timer = 60
            return
        if not all(d.can_be_used(card.dice_requirement) for d in selected):
            self.message = "Не подходит кубик!"
            self.message_timer = 60
            return
        for d in selected:
            card.assigned_dice.append(d.value)
            d.used = True
            d.selected = False
        # Активация
        battle_mgr = BattleManager({'hp': self.player_hp, 'max_hp': self.player_max_hp, 'block': self.player_block},
                                   self.current_enemy, self.dice_list, self.battle_hand, self.particles)
        messages = battle_mgr.activate_card(card)
        # Синхронизация HP и блока после применения карты
        self.player_hp = battle_mgr.player['hp']
        self.player_block = battle_mgr.player['block']
        # Визуальные эффекты
        for msg in messages:
            if "урона" in msg:
                self.enemy_damage_flash_timer = 15
            if "HP" in msg or "блок" in msg:
                self.heal_flash_timer = 15
        self.message = f"{card.name}: " + " | ".join(messages) if messages else f"{card.name}: применено!"
        self.message_timer = 90
        self.player_health.update(self.player_hp, self.player_block)
        if self.enemy_health:
            self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
        if self.current_enemy and self.current_enemy.dead:
            self._enemy_defeated()
        else:
            # Автоматическое завершение хода если все кубики использованы
            unused_dice = [d for d in self.dice_list if not d.used]
            if not unused_dice:
                self.message = "Все кубики использованы!"
                self.message_timer = 60
                self.turn = "ENEMY"
                self.turn_mgr.start_enemy_turn(self._enemy_turn)

    def _init_shop_state(self):
        """Инициализация состояния магазина"""
        self.inventory_cards = self.inv_mgr.cards
        self.selected_upgrade_card = None
        self.upgrade_flash_timer = 0
        self.shop_buttons = {
            'next_floor': Button(SCREEN_WIDTH // 2 - 80, 700, 160, 50, "На карту", BLUE),
            'upgrade': Button(450, 700, 120, 40, "Улучшить", GREEN),
            'cancel': Button(580, 700, 120, 40, "Отмена", RED),
        }

    def _enemy_defeated(self):
        """Победа над врагом"""
        # Расчёт золота с прогрессией
        if self.floor in BOSS_FLOORS:
            gold_gained = 30 + self.floor * 5  # Боссы: 55, 80, 105
        else:
            gold_gained = 10 + self.floor * 2  # Обычные враги: 12, 14, 16...
        
        self.inv_mgr.gold += gold_gained
        self.message = f"Победа! +{gold_gained} золота"
        # Сброс всех карт для нового боя
        for card in self.inv_mgr.cards:
            card.used_this_turn = False
            card.assigned_dice = []
            card.selected_for_battle = False
        # Скрыть тултип карты
        self.card_tooltip_visible = False
        self.card_tooltip_card = None
        
        # Проверяем, был ли это босс
        is_boss = self.floor in BOSS_FLOORS
        
        if is_boss:
            # Показать выбор награды после босса
            self.reward_cards = self.event_mgr.generate_reward_cards(True)
            self.game_state = "REWARD"
        else:
            # Обычный враг - показать выбор активностей
            self.event_choices = self.event_mgr.get_event_choices()
            self.game_state = "EVENT_CHOICE"

    def _enemy_turn(self):
        """Ход врага"""
        if not self.current_enemy or self.current_enemy.dead: return
        battle_mgr = BattleManager({'hp': self.player_hp, 'max_hp': self.player_max_hp, 'block': self.player_block},
                                   self.current_enemy, self.dice_list, self.battle_hand, self.particles)
        dmg, special = battle_mgr.enemy_attack(self.inv_mgr.equipped_armor)
        # Обновляем HP после атаки
        self.player_hp = battle_mgr.player['hp']
        self.player_block = battle_mgr.player['block']
        if dmg > 0:
            self.hero_damage_flash_timer = 15
            self.message = f"{dmg} урона! {special}".strip()
        self.player_health.update(self.player_hp, self.player_block)
        if self.player_hp <= 0:
            self.game_state = "GAME_OVER"
        else:
            # Сброс и новый ход
            for c in self.battle_hand: c.reset_turn()
            self._roll_dice()
            self.turn_mgr.end_enemy_turn()
            self.turn = "PLAYER"
            self.message = "Ваш ход!"
            self.message_timer = 120

    def _roll_dice(self):
        """Бросок кубиков"""
        self.dice_count = get_dice_count_by_floor(self.floor)
        self.dice_list = [Dice(UI_POSITIONS['dice_zone'][0] + 25 + i * 85, UI_POSITIONS['dice_zone'][1] + 20)
                          for i in range(self.dice_count)]
        for d in self.dice_list: d.roll()

    def _visit_location(self, node_type: str):
        """Посещение локации"""
        if node_type in ("enemy", "boss"):
            # Переход к экрану выбора карт (PRE_BATTLE)
            self.inventory_cards = list(self.inv_mgr.cards)  # Копия списка
            self.card_tooltip_visible = False
            self.card_tooltip_card = None
            # Сбрасываем выбор карт для боя
            for card in self.inventory_cards:
                card.selected_for_battle = False
            self.game_state = "PRE_BATTLE"
        elif node_type == "shop":
            self.shop_cards = self.event_mgr.generate_shop_cards()
            self._init_shop_state()
            self.game_state = "SHOP"
        elif node_type == "shop":
            self.shop_cards = self.event_mgr.generate_shop_cards()
            self._init_shop_state()
        # ... остальные типы

    def _init_test_enemies(self):
        """Инициализация списка всех врагов для тестирования"""
        from modules.config.map_config import LOCATIONS
        self.test_enemies = []
        for loc_key, loc_data in LOCATIONS.items():
            # Обычные враги
            for name, hp, dmg_min, dmg_max, icon, dmg_type in loc_data["enemies"]:
                enemy_type = "spirit" if "дух" in name.lower() else "normal"
                self.test_enemies.append({
                    "name": name, "hp": hp, "dmg": (dmg_min, dmg_max),
                    "icon": icon, "dmg_type": dmg_type, "enemy_type": enemy_type
                })
            # Босс
            name, hp, dmg_min, dmg_max, icon, dmg_type = loc_data["boss"]
            enemy_type = "spirit" if "дух" in name.lower() else "boss"
            self.test_enemies.append({
                "name": name, "hp": hp, "dmg": (dmg_min, dmg_max),
                "icon": icon, "dmg_type": dmg_type, "enemy_type": enemy_type
            })

    def _start_battle(self):
        """Начало боя"""
        self.game_state = "BATTLE"
        # Используем врага, который был показан на карте
        self.current_enemy = self.next_enemy
        self.enemy_health = HealthBar(UI_POSITIONS['enemy_hp'][0], UI_POSITIONS['enemy_hp'][1],
                                      250, 30, self.current_enemy.max_hp, RED)
        self.battle_hand = self.inv_mgr.get_battle_hand()
        # Сброс состояния карт перед боем
        for card in self.battle_hand:
            card.reset_turn()
            card.selected_for_battle = False
        for card in self.inv_mgr.cards:
            card.reset_turn()
            card.selected_for_battle = False
        self._roll_dice()
        self.message = f"Бой! {self.current_enemy.name}"

    def _create_enemy(self, floor: int) -> Enemy:
        """Создание врага для этажа (рандомное для обычных боев, фиксированное для боссов)"""
        import random
        from modules.config.map_config import LOCATIONS, get_location_by_floor, get_stage_by_floor, get_boss_floor
        
        # Определяем локацию по этажу
        location_key = get_location_by_floor(floor)
        location_data = LOCATIONS[location_key]
        
        # Проверяем, босс ли это
        stage = get_stage_by_floor(floor)
        boss_floor = get_boss_floor(stage)
        is_boss = (floor == boss_floor)
        
        # Коэффициент сложности по этажу (базовый = 1.0, растёт с этажом)
        difficulty_mult = 1.0 + (floor - 1) * 0.15
        
        if is_boss:
            # Босс - используем фиксированного босса локации
            name, base_hp, base_dmg_min, base_dmg_max, icon, dmg_type = location_data["boss"]
            # Боссы имеют повышенный множитель (x1.5 от обычной сложности этажа)
            hp = int(base_hp * difficulty_mult * 1.5)
            dmg_min = int(base_dmg_min * difficulty_mult * 1.3)
            dmg_max = int(base_dmg_max * difficulty_mult * 1.3)
            # Босс-дух имеет тип spirit, иначе boss
            enemy_type = "spirit" if "дух" in name.lower() else "boss"
        else:
            # Обычный враг - рандомный выбор из списка локации
            name, base_hp, base_dmg_min, base_dmg_max, icon, dmg_type = random.choice(location_data["enemies"])
            hp = int(base_hp * difficulty_mult)
            dmg_min = int(base_dmg_min * difficulty_mult)
            dmg_max = int(base_dmg_max * difficulty_mult)
            # Определяем тип врага: духи имеют особую логику урона
            if "дух" in name.lower():
                enemy_type = "spirit"
            else:
                enemy_type = "normal"
        
        return Enemy(
            name=name,
            hp=hp,
            damage_range=(dmg_min, dmg_max),
            image_path=f"assets/images/{icon}.png",
            icon_type=icon,
            enemy_type=enemy_type,
            damage_type=dmg_type
        )

    def _update(self):
        """Обновление состояния"""
        if self.message_timer > 0: self.message_timer -= 1
        self.particles.update()
        # Обновление таймеров визуальных эффектов
        if self.heal_flash_timer > 0: self.heal_flash_timer -= 1
        if self.hero_damage_flash_timer > 0: self.hero_damage_flash_timer -= 1
        if self.enemy_damage_flash_timer > 0: self.enemy_damage_flash_timer -= 1
        # Обновление hover для карт в инвентаре
        if self.game_state == "INVENTORY":
            for card in self.inventory_cards:
                card.check_hover(pygame.mouse.get_pos())

    # === ОТРИСОВКА ===

    def draw(self):
        # Синхронизация золота с инвентарём
        self.gold = self.inv_mgr.gold
        """
        Универсальная отрисовка через GameRenderer
        Все параметры передаются через **kwargs
        """
        # === ОБЩИЕ ПАРАМЕТРЫ ДЛЯ ВСЕХ СОСТОЯНИЙ ===
        common_params = {
            'floor': self.floor,
            'max_floor': self.max_floor,
            'player_hp': self.player_hp,
            'player_max_hp': self.player_max_hp,
            'dice_count': self.dice_count,
            'inventory_size': len(self.inventory_cards),
            'total_wins': self.total_wins,
            'message': self.message,
            'inventory_cards': self.inventory_cards,
            'inventory_armor': self.inventory_armor,
            'equipped_armor': self.equipped_armor,
        }

        # === ОТРИСОВКА ПО СОСТОЯНИЮ ===
        if self.game_state == "MENU":
            GameRenderer.draw_menu(self.screen, self.start_btn)

        elif self.game_state == "MAP":
            # Используем сохранённого врага
            GameRenderer.draw_map(
                self.screen,
                [],  # Узлы карты больше не рисуются
                self.floor,
                self.player_hp,
                self.player_max_hp,
                self.gold,
                self.inventory_btn,
                self.message,
                self.next_enemy,
                self.fight_from_map_btn
            )
            # Тестовая кнопка и меню выбора врага
            self.test_enemy_btn.draw(self.screen)
            if self.test_enemy_menu_visible:
                menu_x, menu_y = SCREEN_WIDTH - 290, 540
                item_h = 35
                visible_count = 8
                menu_h = visible_count * item_h + 10
                menu_bg = pygame.Rect(menu_x, menu_y, 270, menu_h)
                pygame.draw.rect(self.screen, DARK_GRAY, menu_bg, border_radius=5)
                pygame.draw.rect(self.screen, WHITE, menu_bg, 2, border_radius=5)
                for i in range(self.test_enemy_scroll, min(self.test_enemy_scroll + visible_count, len(self.test_enemies))):
                    enemy = self.test_enemies[i]
                    btn_rect = pygame.Rect(menu_x, menu_y + (i - self.test_enemy_scroll) * item_h, 270, item_h)
                    color = RED if enemy["enemy_type"] == "boss" else (YELLOW if enemy["enemy_type"] == "spirit" else WHITE)
                    pygame.draw.rect(self.screen, color if btn_rect.collidepoint(pygame.mouse.get_pos()) else DARK_BLUE, btn_rect, border_radius=3)
                    text = _ensure_fonts()['tiny'].render(enemy["name"], True, WHITE)
                    self.screen.blit(text, (menu_x + 10, menu_y + (i - self.test_enemy_scroll) * item_h + 10))

        elif self.game_state == "INVENTORY":
            # Обновляем данные перед отрисовкой
            self.inventory_cards = self.inv_mgr.cards
            self.inventory_armor = self.inv_mgr.armor
            self.equipped_armor = self.inv_mgr.equipped_armor
            GameRenderer.draw_inventory(
                self.screen,
                self.inventory_cards,
                self.inventory_armor,
                self.equipped_armor,
                self.map_btn,
                self.message,
                self.armor_tooltip_visible,
                self.armor_tooltip_pos,
                self.armor_tooltip_armor,
                self.inventory_tab,
                self.inventory_scroll
            )

        elif self.game_state == "PRE_BATTLE":
            # Обновляем данные
            self.inventory_cards = list(self.inv_mgr.cards)
            selected = [c for c in self.inventory_cards if c.selected_for_battle]
            GameRenderer.draw_pre_battle(
                self.screen,
                self.inventory_cards,
                selected,
                self.floor,
                self.fight_btn
            )

        elif self.game_state == "BATTLE":
            GameRenderer.draw_battle(
                self.screen,
                self.player_icon,
                self.player_health,
                self.gold,
                self.dice_list,
                self.battle_hand,
                self.end_turn_btn,
                self.turn,
                self.message,
                self.current_enemy,
                self.enemy_health,
                self.enemy_info_visible,
                self.enemy_info_pos,
                self.heal_flash_timer,
                self.hero_damage_flash_timer,
                self.enemy_damage_flash_timer,
                self.floor,
                self.dice_count,
                self.total_wins
            )
            # [TEST] Кнопка убийства врага
            self.kill_enemy_btn.draw(self.screen)
            # Отрисовка частиц (если используете ParticleSystem)
            if hasattr(self, 'particles'):
                self.particles.draw(self.screen)

        elif self.game_state == "REWARD":
            GameRenderer.draw_reward_screen(
                self.screen,
                self.reward_cards,
                self.floor,
                self.dice_count,
                len(self.inventory_cards),
                self.total_wins
            )

        elif self.game_state == "SHOP":
            # Обновляем данные перед отрисовкой
            self.inventory_cards = self.inv_mgr.cards
            self.gold = self.inv_mgr.gold
            GameRenderer.draw_shop(
                self.screen,
                self.shop_cards,
                self.inventory_cards,
                self.gold,
                self.selected_upgrade_card,
                self.upgrade_flash_timer,
                self.shop_buttons,
                self.message
            )
            self.to_map_btn.draw(self.screen)

        elif self.game_state == "TREASURE":
            GameRenderer.draw_treasure(
                self.screen,
                self.treasure_items
            )
            self.to_map_btn.draw(self.screen)

        elif self.game_state == "CAMPFIRE":
            GameRenderer.draw_campfire(
                self.screen,
                self.message
            )
            self.to_map_btn.draw(self.screen)

        elif self.game_state == "EVENT_CHOICE":
            GameRenderer.draw_event_choice(
                self.screen,
                self.event_choices
            )

        elif self.game_state == "GAME_OVER":
            GameRenderer.draw_game_over(
                self.screen,
                self.floor,
                self.total_wins,
                self.next_floor_btn
            )

        elif self.game_state == "VICTORY":
            GameRenderer.draw_victory(
                self.screen,
                self.total_wins,
                self.next_floor_btn
            )

        # === ОБНОВЛЕНИЕ ЭКРАНА ===
        pygame.display.flip()

    # Алиас для обратной совместимости
    _draw = draw