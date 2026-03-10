import pygame
import sys
import random
import os
from modules.settings import *
from modules.utils import FONTS, IconRenderer
from modules.entities import Dice, Enemy, CharacterIcon, Armor
from modules.cards import AbilityCard
from modules.ui import HealthBar, Button


class MapNode:
    def __init__(self, col, row, node_type):
        self.col = col
        self.row = row
        self.type = node_type
        self.x = MAP_START_X + col * NODE_SPACING_X
        self.y = MAP_START_Y + row * NODE_SPACING_Y
        self.visited = False
        self.active = False
        self.rect = pygame.Rect(self.x - 30, self.y - 30, 60, 60)

    def draw(self, screen):
        color = GREEN if self.active else GRAY if self.visited else WHITE
        pygame.draw.circle(screen, color, (self.x, self.y), 30)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), 30, 2)

        icon = "⚔️" if self.type == "enemy" else "🛒" if self.type == "shop" else "🎁" if self.type == "treasure" else "🔥" if self.type == "campfire" else "👹"
        text = FONTS['small'].render(icon, True, BLACK)
        screen.blit(text, (self.x - 10, self.y - 10))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dicey Dungeons - Map Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # Прогресс
        self.floor = 1
        self.max_floor = MAX_FLOOR
        self.total_wins = 0

        # Статы
        self.player_max_hp = PLAYER_MAX_HP
        self.player_hp = PLAYER_MAX_HP
        self.player_block = 0
        self.dice_count = DICE_COUNT
        self.gold = STARTING_GOLD

        # Инвентарь
        self.inventory_cards = []
        self.inventory_armor = []
        self.equipped_armor = None
        self.battle_hand = []

        # Карта
        self.map_nodes = []
        self.current_node_index = 0

        # Объекты
        self.dice_list = []
        self.current_enemy = None
        self.turn = "PLAYER"
        self.message = ""
        self.message_timer = 0
        self.game_state = "MENU"
        self.enemy_defeated_pending = False

        # Визуальные эффекты
        self.heal_flash_timer = 0
        self.hero_damage_flash_timer = 0
        self.enemy_damage_flash_timer = 0
        self.upgrade_flash_timer = 0

        # Информация о враге
        self.enemy_info_visible = False
        self.enemy_info_timer = 0
        self.enemy_info_pos = (0, 0)

        # UI
        self.setup_ui()
        self.create_starting_inventory()
        self.setup_player_icon()

        # ✅ Сброс таймера при старте
        pygame.time.set_timer(pygame.USEREVENT, 0)

    def setup_ui(self):
        self.player_health = HealthBar(UI_POSITIONS['hero_hp'][0], UI_POSITIONS['hero_hp'][1], 200, 30,
                                       self.player_max_hp, GREEN)
        self.enemy_health = None
        self.start_btn = Button(UI_POSITIONS['start_btn_center'] - 100, 380, 200, 60, "Начать игру", GREEN)
        self.next_floor_btn = Button(UI_POSITIONS['restart_btn_center'] - 100, 550, 200, 60, "Заново", GREEN)
        self.end_turn_btn = Button(UI_POSITIONS['end_turn_btn'][0], UI_POSITIONS['end_turn_btn'][1],
                                   UI_POSITIONS['end_turn_btn'][2], UI_POSITIONS['end_turn_btn'][3], "Завершить ход",
                                   BLUE)

        self.inventory_btn = Button(1050, 20, 130, 40, "Инвентарь", BLUE)
        self.map_btn = Button(1050, 70, 130, 40, "Карта", BLUE)

        self.shop_buttons = {
            'next_floor': Button(500, 720, 200, 50, "На карту", GREEN),
            'upgrade': Button(600, 720, 150, 50, "Апгрейд", BLUE),
            'cancel': Button(450, 720, 150, 50, "Отмена", RED),
        }
        self.dice_zone = pygame.Rect(*UI_POSITIONS['dice_zone'])
        self.card_zone = pygame.Rect(*UI_POSITIONS['card_zone'])
        self.selected_upgrade_card = None
        self.last_click_time = 0
        self.last_click_pos = None
        self.double_click_threshold = 300

    def setup_player_icon(self):
        self.player_icon = CharacterIcon(UI_POSITIONS['hero_icon'][0], UI_POSITIONS['hero_icon'][1], 80,
                                         "assets/hero.png", "hero")

    def create_starting_inventory(self):
        self.inventory_cards = []
        for card_data in STARTING_INVENTORY:
            card = AbilityCard(*card_data)
            # ✅ Гарантированный сброс
            card.used_this_turn = False
            card.assigned_dice = []
            self.inventory_cards.append(card)

        self.inventory_armor = []
        start_armor = Armor("Старая одежда", 0, 0, "normal", "armor_metal_0.png")
        self.inventory_armor.append(start_armor)
        self.equipped_armor = start_armor

    def generate_map(self):
        """Генерация карты с ВЫБОРОМ из нескольких путей"""
        self.map_nodes = []

        for col in range(MAP_COLS):
            if col == 0:
                # Первая колонка — только старт (враг)
                node = MapNode(col, 1, "enemy")
                self.map_nodes.append(node)
            elif col == MAP_COLS - 1:
                # Последняя колонка — только босс
                node = MapNode(col, 1, "boss")
                self.map_nodes.append(node)
            else:
                # ✅ Средние колонки — 3 узла с РАЗНЫМИ локациями
                # Узел 1: Враг
                node1 = MapNode(col, 0, "enemy")
                self.map_nodes.append(node1)

                # Узел 2: Случайная локация (магазин/сокровище/костёр)
                random_type = random.choice(["shop", "treasure", "campfire"])
                node2 = MapNode(col, 1, random_type)
                self.map_nodes.append(node2)

                # Узел 3: Враг
                node3 = MapNode(col, 2, "enemy")
                self.map_nodes.append(node3)

        # Активируем только первый узел
        if self.map_nodes:
            self.map_nodes[0].active = True
            self.current_node_index = 0

    def start_new_game(self):
        self.phase = "BATTLE"
        self.floor = 1
        self.player_hp = PLAYER_MAX_HP
        self.player_max_hp = PLAYER_MAX_HP
        self.dice_count = DICE_COUNT
        self.gold = STARTING_GOLD
        self.total_wins = 0
        self.heal_flash_timer = 0
        self.hero_damage_flash_timer = 0
        self.enemy_damage_flash_timer = 0
        self.upgrade_flash_timer = 0
        self.enemy_info_visible = False
        self.enemy_info_timer = 0
        self.create_starting_inventory()
        self.generate_map()
        self.game_state = "MAP"

    def enter_battle_preparation(self):
        """Подготовка к бою"""
        self.game_state = "PRE_BATTLE"
        self.battle_hand = []
        self.message = "Выберите карты для боя (0-5)"

        # ✅ СБРОС флагов
        self.enemy_defeated_pending = False
        self.turn = "PLAYER"

        # Сброс всех карт
        for card in self.inventory_cards:
            card.used_this_turn = False
            card.assigned_dice = []
            card.hovered = False

        print(f"📋 Подготовка к бою: этаж {self.floor}, карт в инвентаре: {len(self.inventory_cards)}")

    def start_battle(self):
        """Начало боя"""
        self.game_state = "BATTLE"
        node = self.map_nodes[self.current_node_index]
        node.visited = True
        node.active = False

        # ✅ СБРОС флагов от предыдущего боя
        self.enemy_defeated_pending = False
        self.turn = "PLAYER"

        self.current_enemy = self.create_enemy_for_floor(self.floor)
        self.enemy_health = HealthBar(UI_POSITIONS['enemy_hp'][0], UI_POSITIONS['enemy_hp'][1], 250, 30,
                                      self.current_enemy.max_hp, RED)
        self.enemy_health.update(self.current_enemy.hp, 0)

        # Сброс всех карт
        for card in self.inventory_cards:
            card.used_this_turn = False
            card.assigned_dice = []
            card.hovered = False

        for card in self.battle_hand:
            card.used_this_turn = False
            card.assigned_dice = []

        self.roll_dice()
        self.message = f"Бой! {self.current_enemy.name}"
        print(f"🎮 Бой начат: этаж {self.floor}, враг {self.current_enemy.name}")

    def roll_dice(self):
        """Бросок кубиков"""
        print(f"roll_dice вызван, карт в руке: {len(self.battle_hand)}")

        self.dice_list = []
        start_x = UI_POSITIONS['dice_zone'][0] + 25
        start_y = UI_POSITIONS['dice_zone'][1] + 20
        for i in range(self.dice_count):
            dice = Dice(start_x + i * 85, start_y)
            dice.roll()
            self.dice_list.append(dice)

        # ✅ Сброс всех карт в руке
        for i, card in enumerate(self.battle_hand):
            print(f"Сброс карты {i}: {card.name}")
            card.reset_turn()

    def get_selected_dice(self):
        return [d for d in self.dice_list if d.selected and not d.used]

    def get_unused_dice(self):
        return [d for d in self.dice_list if not d.used]

    def check_auto_end_turn(self):
        if len(self.get_unused_dice()) == 0 and self.turn == "PLAYER" and self.current_enemy and not self.current_enemy.dead:
            self.message = "Все кубики использованы! Ход врага..."
            self.message_timer = 60
            self.end_player_turn()

    def assign_dice_to_card(self, card):
        selected_dice = self.get_selected_dice()
        if len(selected_dice) != card.dice_cost:
            self.message = f"Нужно {card.dice_cost} кубика!"
            self.message_timer = 60
            return False
        for dice in selected_dice:
            if not dice.can_be_used(card.dice_requirement):
                self.message = f"Не подходит кубик {dice.value}!"
                self.message_timer = 60
                return False
        for dice in selected_dice:
            card.assigned_dice.append(dice.value)
            dice.used = True
            dice.selected = False
        self.message = f"{card.name} активирована!"
        self.message_timer = 60
        self.activate_card(card)
        self.check_auto_end_turn()
        return True

    def calculate_type_damage(self, attack_type, base_damage):
        """Расчёт урона с учётом типов"""
        if not self.current_enemy:
            return base_damage

        enemy_element = getattr(self.current_enemy, 'damage_type', 'normal')
        enemy_type = getattr(self.current_enemy, 'enemy_type', 'normal')

        multiplier = TYPE_EFFECTIVENESS.get(attack_type, {}).get(enemy_element, 1.0)

        if enemy_type == "spirit":
            if attack_type == "normal":
                multiplier = 0
                self.message += " | ИММУНИТЕТ!"
            else:
                multiplier *= 2
                self.message += " | ЭФФЕКТИВНО!"

        elif enemy_type == "elemental":
            if attack_type != "normal":
                multiplier = 0
                self.message += " | ИММУНИТЕТ!"
            else:
                multiplier *= 2
                self.message += " | ЭФФЕКТИВНО!"

        final_damage = int(base_damage * multiplier)

        if multiplier > 1.0 and enemy_type not in ["spirit", "elemental"]:
            self.message += f" | ЭФФЕКТИВНО! x{multiplier}"
        elif multiplier < 1.0 and multiplier > 0:
            self.message += f" | СЛАБО! x{multiplier}"

        return max(0, final_damage)

    def calculate_armor_effect(self, damage, enemy_type):
        """Расчёт урона с учётом брони"""
        if not self.equipped_armor:
            return damage

        reduced_dmg = max(0, damage - self.equipped_armor.defense)

        if self.equipped_armor.armor_type == "elemental" and self.equipped_armor.element:
            mult = TYPE_EFFECTIVENESS.get(self.equipped_armor.element, {}).get(enemy_type, 1.0)
            if mult > 1.0:
                reflect_dmg = int(self.equipped_armor.defense * mult)
                if self.current_enemy:
                    self.current_enemy.take_damage(reflect_dmg)
                    self.message += f" | Отражение {reflect_dmg}!"

        return reduced_dmg

    def activate_card(self, card):
        """ПОЛНОСТЬЮ ИСПРАВЛЕНО: Все эффекты работают корректно"""
        effect = card.calculate_effect()
        if self.current_enemy is None or self.current_enemy.dead:
            return

        message_parts = []
        attack_type = getattr(card, 'damage_type', 'normal')

        # НАНЕСЕНИЕ УРОНА
        if "damage" in effect and effect["damage"] > 0:
            base_damage = effect["damage"]
            calculated_dmg = self.calculate_type_damage(attack_type, base_damage)
            actual_dmg = self.current_enemy.take_damage(calculated_dmg)

            if self.enemy_health:
                self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
            self.enemy_damage_flash_timer = 10

            type_names = {
                "normal": "", "fire": "[Огонь] ", "water": "[Вода] ",
                "electric": "[Молния] ", "grass": "[Природа] ", "ground": "[Земля] "
            }
            message_parts.append(f"{type_names.get(attack_type, '')}{actual_dmg} урона")

        # ПОЛУЧЕНИЕ БЛОКА
        if "block" in effect and effect["block"] > 0:
            block_amount = effect["block"]
            self.player_block += block_amount
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            self.heal_flash_timer = 10
            message_parts.append(f"+{block_amount} блок")

        # ЛЕЧЕНИЕ
        if "heal" in effect and effect["heal"] > 0:
            heal_amount = effect["heal"]
            self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            self.heal_flash_timer = 10
            message_parts.append(f"+{heal_amount} HP")

        # ФОРМИРОВАНИЕ СООБЩЕНИЯ
        if message_parts:
            self.message = f"{card.name}: " + " | ".join(message_parts)
        else:
            self.message = f"{card.name}: эффект применён!"

        # ПРОВЕРКА СМЕРТИ ВРАГА
        if self.current_enemy and self.current_enemy.dead:
            self.enemy_defeated()

        # ПОМЕТКА КАРТЫ
        card.mark_used()
        self.message_timer = 90

        # ✅ Проверка - не помечать все карты
        # Уберите если есть код типа:
        # for c in self.battle_hand:
        #     c.used_this_turn = True

    def enemy_defeated(self):
        """Победа над врагом"""
        self.message = f"{self.current_enemy.name} побеждён!"
        self.message_timer = 120
        self.enemy_defeated_pending = True  # <-- Ставим True для обработки

        is_boss = self.is_boss_floor()
        if is_boss:
            self.gold += GOLD_PER_BOSS
            self.message = f"БОСС побеждён! +{GOLD_PER_BOSS}G!"
        else:
            self.gold += GOLD_PER_VICTORY
            self.message = f"Победа! +{GOLD_PER_VICTORY}G"

        # Сброс карт
        for card in self.inventory_cards:
            card.used_this_turn = False
            card.assigned_dice = []

        if self.floor >= self.max_floor:
            self.game_state = "VICTORY"
        else:
            self.game_state = "REWARD"
            self.generate_reward_cards()

        # ✅ Флаг сбрасывается когда переходим в REWARD и потом в MAP
        # Но на всякий случай добавим сброс при смене game_state
        print(f"🏆 enemy_defeated(): game_state={self.game_state}, pending={self.enemy_defeated_pending}")

    def generate_event_choice(self):
        """Генерация выбора события после награды"""
        self.event_choices = [
            {"type": "shop", "name": "Магазин", "icon": "🛒"},
            {"type": "treasure", "name": "Сокровищница", "icon": "🎁"},
            {"type": "campfire", "name": "Костёр", "icon": "🔥"}
        ]
        self.game_state = "EVENT_CHOICE"

    def create_enemy_for_floor(self, floor):
        """Создание врага с учётом этапа (региона)"""
        is_boss = floor in BOSS_FLOORS

        if floor <= 5:
            stage = 1
        elif floor <= 10:
            stage = 2
        else:
            stage = 3

        if is_boss:
            boss_enemies = [
                ("ДРЕВНИЙ ДУХ", 120, (8, 12), "assets/forest_spirit.png", None, "spirit", "spirit", "normal"),
                ("КРАКЕН", 180, (10, 15), "assets/kraken.png", None, "kraken", "elemental", "water"),
                ("ПОВЕЛИТЕЛЬ ЛАВЫ", 250, (12, 18), "assets/lava_golem.png", "fire", "golem", "elemental", "fire"),
            ]
            boss_idx = (floor // 5 - 1) % len(boss_enemies)
            boss = boss_enemies[boss_idx]
            return Enemy(boss[0], boss[1], boss[2], boss[3], boss[4], boss[5], boss[6], boss[7])
        else:
            if stage == 1:
                normal_enemies = [
                    (1, "Слайм", 25, (2, 4), "assets/slime.png", None, "slime", "normal", "normal"),
                    (2, "Гоблин", 30, (3, 5), "assets/goblin.png", None, "goblin", "normal", "normal"),
                    (3, "Волк", 35, (4, 6), "assets/wolf.png", None, "wolf", "normal", "normal"),
                    (4, "Энт", 45, (5, 8), "assets/treant.png", None, "treant", "normal", "normal"),
                    (5, "Лесной дух", 40, (4, 7), "assets/forest_spirit.png", None, "spirit", "spirit", "normal"),
                ]
            elif stage == 2:
                normal_enemies = [
                    (6, "Водяной слайм", 55, (5, 8), "assets/water_slime.png", None, "slime", "normal", "water"),
                    (7, "Рыбочеловек", 60, (6, 9), "assets/fish_man.png", None, "fishman", "normal", "water"),
                    (8, "Черепаха", 70, (5, 7), "assets/turtle.png", "block", "turtle", "normal", "water"),
                    (9, "Водяной дух", 65, (6, 10), "assets/water_spirit.png", None, "spirit", "spirit", "water"),
                    (10, "Нага", 75, (7, 11), "assets/naga.png", None, "naga", "normal", "water"),
                ]
            else:
                normal_enemies = [
                    (11, "Огненный слайм", 85, (7, 10), "assets/fire_slime.png", "fire", "slime", "normal", "fire"),
                    (12, "Лавовый голем", 110, (8, 12), "assets/lava_golem.png", "fire", "golem", "elemental", "fire"),
                    (13, "Огненный дух", 95, (8, 11), "assets/fire_spirit.png", "fire", "spirit", "spirit", "fire"),
                    (14, "Магмовый зверь", 120, (9, 13), "assets/magma_beast.png", "fire", "beast", "normal", "fire"),
                    (15, "Огненный дракон", 130, (10, 15), "assets/fire_dragon.png", "fire", "dragon", "elemental",
                     "fire"),
                ]

            enemy_idx = (floor - 1) % len(normal_enemies)
            enemy = normal_enemies[enemy_idx]
            return Enemy(enemy[1], enemy[2], enemy[3], enemy[4], enemy[5], enemy[6], enemy[7], enemy[8])

    def is_boss_floor(self):
        return self.floor in BOSS_FLOORS

    def check_dice_milestone(self):
        if self.total_wins in DICE_MILESTONES:
            self.dice_count += 1
            return True
        return False

    def generate_reward_cards(self):
        self.reward_cards = []
        is_boss = self.floor in BOSS_FLOORS

        if is_boss:
            available_cards = list(TIER_4_CARDS)
            for _ in range(3):
                if not available_cards:
                    break
                card_data = random.choice(available_cards)
                available_cards.remove(card_data)
                card = AbilityCard(*card_data)
                self.reward_cards.append(card)
            return

        all_tier_cards = []
        all_tier_cards.extend([(c, 0) for c in TIER_0_CARDS])
        all_tier_cards.extend([(c, 1) for c in TIER_1_CARDS])
        all_tier_cards.extend([(c, 2) for c in TIER_2_CARDS])

        weights = []
        for _, tier in all_tier_cards:
            weights.append(REWARD_CHANCES[tier])

        for _ in range(3):
            if not all_tier_cards:
                break
            idx = random.choices(range(len(all_tier_cards)), weights=weights)[0]
            card_data = all_tier_cards[idx][0]
            card = AbilityCard(*card_data)
            self.reward_cards.append(card)

    def generate_shop_cards(self):
        self.shop_cards = []
        available_cards = list(SHOP_CARDS)

        for _ in range(4):
            if not available_cards:
                break
            card_data = random.choice(available_cards)
            available_cards.remove(card_data)
            card = AbilityCard(*card_data)
            self.shop_cards.append(card)

    def generate_treasure(self):
        """Генерация сокровищ"""
        self.treasure_items = []
        if random.random() > 0.5:
            # Броня
            tier = random.choice([1, 2])
            data = ARMOR_TIERS[tier].copy()  # Копируем данные
            data["tier"] = tier  # ✅ Добавляем tier в данные
            self.treasure_items.append({"type": "armor", "data": data})
        else:
            # Карта
            data = random.choice(TIER_1_CARDS + TIER_2_CARDS)
            self.treasure_items.append({"type": "card", "data": data})

    def heal_at_campfire(self):
        self.player_max_hp += 10
        self.player_hp = self.player_max_hp
        self.player_health.max_hp = self.player_max_hp
        self.player_health.update(self.player_hp, 0)
        self.message = "Костёр: +10 Макс HP и полное лечение!"

    def visit_location(self):
        node = self.map_nodes[self.current_node_index]
        if node.type == "shop":
            self.game_state = "SHOP"
            self.generate_shop_cards()
        elif node.type == "treasure":
            self.game_state = "TREASURE"
            self.generate_treasure()
        elif node.type == "campfire":
            self.game_state = "CAMPFIRE"
            self.heal_at_campfire()
        elif node.type == "enemy" or node.type == "boss":
            self.enter_battle_preparation()

    def move_to_next_node(self):
        """Возврат на карту после награды"""
        current_col = self.map_nodes[self.current_node_index].col

        # ✅ Находим ВСЕ узлы следующей колонки
        next_nodes = [n for n in self.map_nodes if n.col == current_col + 1]

        if next_nodes:
            # Деактивируем текущий узел
            self.map_nodes[self.current_node_index].active = False
            self.map_nodes[self.current_node_index].visited = True

            # ✅ Активируем ВСЕ узлы следующей колонки (даёт выбор!)
            for node in next_nodes:
                node.active = True

            self.floor += 1
            self.game_state = "MAP"  # ✅ Возврат на карту, а не авто-переход
        else:
            # Конец карты
            self.game_state = "VICTORY"

    def end_player_turn(self):
        """Завершение хода игрока"""
        if self.current_enemy and self.current_enemy.dead:
            return

        self.turn = "ENEMY"
        self.message = f"Ход {self.current_enemy.name}..."
        self.message_timer = 60

        # ✅ СБРОС и УСТАНОВКА таймера
        pygame.time.set_timer(pygame.USEREVENT, 0)  # Сброс
        pygame.time.set_timer(pygame.USEREVENT, 1500)  # Установка
        print(f"✅ Таймер хода врага установлен: 1500мс")

    def enemy_turn(self):
        """Ход врага"""
        print(f"🎯 enemy_turn() вызван")
        print(f"   - current_enemy: {self.current_enemy.name if self.current_enemy else 'None'}")
        print(f"   - current_enemy.dead: {self.current_enemy.dead if self.current_enemy else 'N/A'}")
        print(f"   - enemy_defeated_pending: {self.enemy_defeated_pending}")
        print(f"   - game_state: {self.game_state}")

        # Проверка условий пропуска
        if not self.current_enemy:
            print("❌ Пропуск: current_enemy is None")
            return
        if self.current_enemy.dead:
            print("❌ Пропуск: враг уже мёртв")
            return
        if self.enemy_defeated_pending:
            print("❌ Пропуск: enemy_defeated_pending = True")
            return

        print("✅ Выполняем атаку врага...")
        dmg, special = self.current_enemy.attack()
        print(f"⚔️ Враг атакует: {dmg} урона, спец: {special}")

        # Применение брони
        if self.equipped_armor:
            enemy_type = getattr(self.current_enemy, 'damage_type', 'normal')
            dmg = self.calculate_armor_effect(dmg, enemy_type)
            print(f"🛡️ После брони: {dmg} урона")

        # Блок
        if self.player_block > 0:
            blocked = min(self.player_block, dmg)
            self.player_block -= blocked
            dmg -= blocked
            self.message = f"Блок: -{blocked} "
            self.player_health.update(self.player_hp, self.player_block)

        # Урон игроку
        if dmg > 0:
            self.player_hp -= dmg
            self.player_health.update(self.player_hp, self.player_block)
            self.message += f"{dmg} урона! {special}"
            self.hero_damage_flash_timer = 10
            print(f"❤️ Игрок получил {dmg} урона, осталось HP: {self.player_hp}")

        # Проверка смерти
        if self.player_hp <= 0:
            self.game_state = "GAME_OVER"
            print("💀 Игрок погиб!")
        else:
            # Возврат хода
            self.turn = "PLAYER"

            # Сброс карт
            for card in self.battle_hand:
                card.used_this_turn = False
                card.assigned_dice = []

            self.roll_dice()
            self.message = "Ваш ход!"
            print("🔄 Ход игрока, карты сброшены")

        self.message_timer = 120
        print("✅ enemy_turn() завершён")

    def check_player_death(self):
        if self.player_hp <= 0:
            self.game_state = "GAME_OVER"
            self.message = f"Погибли на этаже {self.floor}!"

    def buy_card(self, card_index):
        if 0 <= card_index < len(self.shop_cards):
            card = self.shop_cards[card_index]
            if self.gold >= card.price:
                self.gold -= card.price
                self.inventory_cards.append(card)
                self.message = f"Куплено: {card.name} за {card.price}G!"
                self.shop_cards.pop(card_index)
            else:
                self.message = "Недостаточно золота!"

    def sell_card(self, card_index):
        if 0 <= card_index < len(self.inventory_cards):
            card = self.inventory_cards[card_index]
            if card.tier >= 4:
                self.message = "Карту 4 разряда нельзя продать!"
                return
            sell_price = card.get_sell_price()
            self.gold += sell_price
            self.inventory_cards.pop(card_index)
            self.message = f"Продано за {sell_price}G!"
            self.selected_upgrade_card = None

    def upgrade_card(self, card_index):
        if 0 <= card_index < len(self.inventory_cards):
            card = self.inventory_cards[card_index]
            if card.tier >= 3:
                self.message = "Максимальный разряд!"
                self.selected_upgrade_card = None
                return

            upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
            if self.gold >= upgrade_cost:
                upgrade_key = (card.name, card.tier)
                if upgrade_key in CARD_UPGRADES:
                    upgrade_name, upgrade_tier = CARD_UPGRADES[upgrade_key]

                    for card_data in TIER_3_CARDS:
                        if card_data[0] == upgrade_name and card_data[9] == upgrade_tier:
                            self.gold -= upgrade_cost
                            new_card = AbilityCard(*card_data)
                            self.inventory_cards[card_index] = new_card
                            self.message = f"Апгрейд: {card.name} → {upgrade_name}!"
                            self.upgrade_flash_timer = 30
                            self.selected_upgrade_card = None
                            return

                    self.message = "Апгрейд не найден!"
                else:
                    self.message = "Нет апгрейда для этой карты!"
            else:
                self.message = f"Нужно {upgrade_cost}G для апгрейда!"

    # === ОТРИСОВКА ===
    def draw_menu(self):
        self.screen.fill(DARK_BLUE)
        title = FONTS['large'].render("Dicey Dungeons", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        subtitle = FONTS['medium'].render("Python Edition", True, LIGHT_GRAY)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
        self.start_btn.draw(self.screen)

    def draw_map(self):
        self.screen.fill(DARK_BLUE)
        title = FONTS['large'].render("Карта приключений", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        for node in self.map_nodes:
            node.draw(self.screen)

        info = FONTS['small'].render(
            f"Этаж: {self.floor} | HP: {self.player_hp}/{self.player_max_hp} | Золото: {self.gold}", True, WHITE)
        self.screen.blit(info, (20, 750))

        self.inventory_btn.draw(self.screen)

        if self.message:
            msg = FONTS['small'].render(self.message, True, WHITE)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 700))

    def draw_inventory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))

        title = FONTS['large'].render("Инвентарь", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        text = FONTS['medium'].render("Карты:", True, WHITE)
        self.screen.blit(text, (50, 120))
        for i, card in enumerate(self.inventory_cards[:10]):
            card.set_position(50 + (i % 5) * 160, 160 + (i // 5) * 200)
            card.draw(self.screen)

        text = FONTS['medium'].render("Броня:", True, WHITE)
        self.screen.blit(text, (50, 550))
        for i, armor in enumerate(self.inventory_armor):
            x = 50 + i * 100
            armor.draw(self.screen, x, 600)
            if self.equipped_armor == armor:
                pygame.draw.rect(self.screen, GREEN, (x - 2, 598, 54, 54), 2)
            name = FONTS['tiny'].render(armor.name, True, WHITE)
            self.screen.blit(name, (x, 650))

        self.map_btn.draw(self.screen)

    def draw_pre_battle(self):
        self.screen.fill(DARK_GRAY)
        title = FONTS['large'].render("Снаряжение в бой", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        count_text = FONTS['medium'].render(f"Выбрано: {len(self.battle_hand)}/5", True, WHITE)
        self.screen.blit(count_text, (SCREEN_WIDTH // 2 - count_text.get_width() // 2, 100))

        # Отрисовка карт
        for i, card in enumerate(self.inventory_cards):
            card.set_position(50 + (i % 8) * 140, 150 + (i // 8) * 200)
            card.draw(self.screen)  # ✅ Метод draw() сам проверит used_this_turn
            if card in self.battle_hand:
                pygame.draw.rect(self.screen, GREEN, (card.x - 2, card.y - 2, card.width + 4, card.height + 4), 2)

        # Кнопка
        start_btn = Button(SCREEN_WIDTH // 2 - 100, 720, 200, 60, "В БОЙ!", RED)
        start_btn.enabled = True
        start_btn.draw(self.screen)

    def draw_battle(self):
        self.screen.fill(DARK_GRAY)

        floor_text = FONTS['medium'].render(f"Этаж {self.floor}/{self.max_floor}", True, GOLD)
        self.screen.blit(floor_text, (SCREEN_WIDTH // 2 - floor_text.get_width() // 2, 10))

        self.player_icon.draw(self.screen)
        player_text = FONTS['small'].render("Герой", True, GREEN)
        self.screen.blit(player_text, (UI_POSITIONS['hero_name'][0], UI_POSITIONS['hero_name'][1]))

        # Эффект лечения
        if self.heal_flash_timer > 0:
            pygame.draw.rect(self.screen, GREEN,
                             (self.player_health.x - 3, self.player_health.y - 3,
                              self.player_health.width + 6, self.player_health.height + 6),
                             3, border_radius=7)

        # Эффект урона по герою
        if self.hero_damage_flash_timer > 0:
            hero_rect = pygame.Rect(UI_POSITIONS['hero_icon'][0] - 5,
                                    UI_POSITIONS['hero_icon'][1] - 5,
                                    90, 90)
            pygame.draw.rect(self.screen, RED, hero_rect, 6, border_radius=15)

        self.player_health.draw(self.screen)

        IconRenderer.draw_gold_icon(self.screen, UI_POSITIONS['hero_gold'][0], UI_POSITIONS['hero_gold'][1], 25)
        gold_text = FONTS['small'].render(f"{self.gold}", True, GOLD)
        self.screen.blit(gold_text, (UI_POSITIONS['hero_gold'][0] + 30, UI_POSITIONS['hero_gold'][1]))

        dice_text = FONTS['tiny'].render(
            f"Кубиков: {self.dice_count} | Карт: {len(self.inventory_cards)} | Победы: {self.total_wins}", True,
            LIGHT_GRAY)
        self.screen.blit(dice_text, (140, 115))

        # === ОТРИСОВКА ПОЛЯ БОЯ ===
        self.draw_battle_field()

        # === СООБЩЕНИЕ ===
        if self.message:
            msg_surface = FONTS['small'].render(self.message, True, WHITE)
            msg_box_width = msg_surface.get_width() + 20
            pygame.draw.rect(self.screen, DARK_BLUE, (SCREEN_WIDTH // 2 - msg_box_width // 2, 730, msg_box_width, 35),
                             border_radius=5)
            self.screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, 735))

    def draw_battle_field(self):
        pygame.draw.rect(self.screen, CARD_BG, self.dice_zone, border_radius=10)
        pygame.draw.rect(self.screen, CARD_BORDER, self.dice_zone, 2, border_radius=10)
        dice_label = FONTS['small'].render("Кубики (клик для выбора)", True, LIGHT_GRAY)
        self.screen.blit(dice_label, (self.dice_zone.x + 10, self.dice_zone.y - 25))
        for dice in self.dice_list:
            dice.draw(self.screen)

        pygame.draw.rect(self.screen, CARD_BG, self.card_zone, border_radius=10)
        pygame.draw.rect(self.screen, CARD_BORDER, self.card_zone, 2, border_radius=10)
        card_label = FONTS['small'].render("Карты (клик после кубика)", True, LIGHT_GRAY)
        self.screen.blit(card_label, (self.card_zone.x + 10, self.card_zone.y - 25))

        card_start_x = self.card_zone.x + 15
        card_spacing = 165
        for i, card in enumerate(self.battle_hand[:5]):
            card.set_position(card_start_x + i * card_spacing, self.card_zone.y + 10)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen)

        self.end_turn_btn.draw(self.screen)

        turn_text = FONTS['medium'].render(f"{'ВАШ ХОД' if self.turn == 'PLAYER' else 'ХОД ВРАГА'}",
                                           True, YELLOW if self.turn == "PLAYER" else RED)
        self.screen.blit(turn_text, (UI_POSITIONS['turn_text'][0], UI_POSITIONS['turn_text'][1]))

        if self.current_enemy:
            if self.enemy_damage_flash_timer > 0:
                enemy_rect = pygame.Rect(UI_POSITIONS['enemy_icon'][0] - 5,
                                         UI_POSITIONS['enemy_icon'][1] - 5,
                                         130, 130)
                pygame.draw.rect(self.screen, RED, enemy_rect, 6, border_radius=15)

            self.enemy_health.draw(self.screen)
            self.current_enemy.draw(self.screen, UI_POSITIONS['enemy_icon'][0], UI_POSITIONS['enemy_icon'][1])

            if self.enemy_info_visible and self.enemy_info_timer > 0:
                self.draw_enemy_info()

    def draw_enemy_info(self):
        if not self.current_enemy:
            return

        info_lines = self.current_enemy.get_info_text()

        max_width = 0
        for line in info_lines:
            text_width = FONTS['tiny'].render(line, True, WHITE).get_width()
            if text_width > max_width:
                max_width = text_width

        box_width = max_width + 20
        box_height = len(info_lines) * 18 + 10

        info_x = min(self.enemy_info_pos[0], SCREEN_WIDTH - box_width - 10)
        info_y = min(self.enemy_info_pos[1], SCREEN_HEIGHT - box_height - 10)

        pygame.draw.rect(self.screen, DARK_BLUE, (info_x, info_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(self.screen, GOLD, (info_x, info_y, box_width, box_height), 2, border_radius=8)

        for i, line in enumerate(info_lines):
            if "ИММУНИТЕТ" in line:
                color = WHITE
            elif "x4.0" in line or "x4" in line:
                color = (180, 100, 255)
            elif "x2.0" in line or "x2" in line:
                color = GREEN
            elif "обычный урон" in line or "x1.0" in line or "x1" in line:
                color = YELLOW
            elif "x0.5" in line:
                color = ORANGE
            elif "x0.25" in line:
                color = RED
            elif "ДУХ:" in line or "ЭЛЕМЕНТАЛЬ:" in line:
                color = GOLD
            elif "Эффективность атак:" in line:
                color = CYAN
            elif "HP:" in line or "Урон:" in line or "Тип:" in line:
                color = CYAN
            else:
                color = WHITE

            text_surf = FONTS['tiny'].render(line, True, color)
            self.screen.blit(text_surf, (info_x + 10, info_y + 5 + i * 18))

    def draw_reward_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))

        title = FONTS['large'].render("ВЫБЕРИТЕ НАГРАДУ!", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        for i, card in enumerate(self.reward_cards):
            card.set_position(180 + i * 270, 280)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen)

        info_text = FONTS['small'].render(
            f"Кубиков: {self.dice_count} | Карт: {len(self.inventory_cards)} | Победы: {self.total_wins}", True,
            LIGHT_GRAY)
        self.screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, 520))

    def draw_shop(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))

        title = FONTS['large'].render("МАГАЗИН", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        IconRenderer.draw_gold_icon(self.screen, SCREEN_WIDTH // 2 - 15, 130, 25)
        gold_text = FONTS['medium'].render(f"{self.gold}", True, GOLD)
        self.screen.blit(gold_text, (SCREEN_WIDTH // 2 + 20, 130))

        buy_title = FONTS['small'].render("Купить карты:", True, WHITE)
        self.screen.blit(buy_title, (150, 170))

        for i, card in enumerate(self.shop_cards):
            card.set_position(150 + i * 200, 210)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen, show_price=True, price_type="buy", player_gold=self.gold)

        sell_title = FONTS['small'].render("Инвентарь (двойной клик для продажи):", True, WHITE)
        self.screen.blit(sell_title, (150, 420))

        start_x = 150
        start_y = 460
        cards_per_row = 6
        for i, card in enumerate(self.inventory_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            card.set_position(start_x + col * 155, start_y + row * 200)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen, show_price=True, price_type="sell", player_gold=self.gold)

            if self.selected_upgrade_card == i:
                pygame.draw.rect(self.screen, BLUE, (card.x - 3, card.y - 3,
                                                     card.width + 6, card.height + 6), 3, border_radius=12)

        if self.upgrade_flash_timer > 0:
            pygame.draw.rect(self.screen, GOLD,
                             (150 - 5, 460 - 5,
                              6 * 155 + 10,
                              max(200, (len(self.inventory_cards) // 6 + 1) * 200 + 10)),
                             4, border_radius=15)

        if self.selected_upgrade_card is not None:
            card = self.inventory_cards[self.selected_upgrade_card]
            upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
            next_tier = card.tier + 1
            upgrade_color = GREEN if self.gold >= upgrade_cost else RED

            upgrade_key = (card.name, card.tier)
            if upgrade_key in CARD_UPGRADES:
                upgrade_name = CARD_UPGRADES[upgrade_key][0]
                upgrade_info = FONTS['small'].render(f"-> {upgrade_name} за ", True, WHITE)
            else:
                upgrade_info = FONTS['small'].render(f"Апгрейд T{next_tier}: ", True, WHITE)

            cost_info = FONTS['small'].render(f"{upgrade_cost}G", True, upgrade_color)
            self.screen.blit(upgrade_info, (450, 670))
            self.screen.blit(cost_info, (650, 670))
            IconRenderer.draw_gold_icon(self.screen, 710, 668, 18)

        self.shop_buttons['next_floor'].draw(self.screen)

        if self.selected_upgrade_card is not None:
            self.shop_buttons['upgrade'].draw(self.screen)
            self.shop_buttons['cancel'].draw(self.screen)
        # Кнопка "На карту" (добавить в конец каждого метода отрисовки события)
        next_btn = Button(SCREEN_WIDTH // 2 - 100, 720, 200, 60, "На карту", GREEN)
        next_btn.draw(self.screen)

    def draw_treasure(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))
        title = FONTS['large'].render("Сокровищница", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        for i, item in enumerate(self.treasure_items):
            if item["type"] == "card":
                card = AbilityCard(*item["data"])
                card.set_position(300 + i * 200, 200)
                card.draw(self.screen)
            elif item["type"] == "armor":
                d = item["data"]
                # ✅ Получаем tier из данных или используем 1 по умолчанию
                tier = d.get("tier", 1)
                armor = Armor(d["name"], tier, d["defense"], d["type"], d["asset"])
                armor.draw(self.screen, 300 + i * 200, 200)

        msg = FONTS['small'].render("Кликните чтобы забрать", True, WHITE)
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 500))

    def draw_campfire(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))
        title = FONTS['large'].render("Костёр", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        msg = FONTS['medium'].render("HP восстановлено! Макс HP +10", True, GREEN)
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 300))
        btn = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 60, "Дальше", GREEN)
        btn.draw(self.screen)
        # Кнопка "На карту" (добавить в конец каждого метода отрисовки события)
        next_btn = Button(SCREEN_WIDTH // 2 - 100, 720, 200, 60, "На карту", GREEN)
        next_btn.draw(self.screen)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        text = FONTS['large'].render("ПОРАЖЕНИЕ", True, RED)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
        info = FONTS['medium'].render(f"Этаж: {self.floor} | Победы: {self.total_wins}", True, WHITE)
        self.screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 360))
        self.next_floor_btn.draw(self.screen)

    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        text = FONTS['large'].render("ПОБЕДА!", True, GOLD)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
        info = FONTS['medium'].render(f"Всего побед: {self.total_wins}", True, WHITE)
        self.screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 360))
        self.next_floor_btn.draw(self.screen)

    def draw_event_choice(self):
        """Отрисовка выбора события"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_BLUE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))

        title = FONTS['large'].render("Выберите следующее событие", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        for i, event in enumerate(self.event_choices):
            x = 200 + i * 270
            rect = pygame.Rect(x, 250, 250, 200)
            pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=10)
            pygame.draw.rect(self.screen, GOLD, rect, 3, border_radius=10)

            icon = FONTS['large'].render(event["icon"], True, WHITE)
            name = FONTS['medium'].render(event["name"], True, WHITE)
            self.screen.blit(icon, (x + 100, 270))
            self.screen.blit(name, (x + 60, 350))

    def draw(self):
        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "MAP":
            self.draw_map()
        elif self.game_state == "INVENTORY":
            self.draw_inventory()
        elif self.game_state == "PRE_BATTLE":
            self.draw_pre_battle()
        elif self.game_state == "BATTLE":
            self.draw_battle()
        elif self.game_state == "REWARD":
            self.draw_reward_screen()
        elif self.game_state == "EVENT_CHOICE":  # ✅ НОВОЕ
            self.draw_event_choice()
        elif self.game_state == "SHOP":
            self.draw_shop()
        elif self.game_state == "TREASURE":
            self.draw_treasure()
        elif self.game_state == "CAMPFIRE":
            self.draw_campfire()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over()
        elif self.game_state == "VICTORY":
            self.draw_victory()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                current_time = pygame.time.get_ticks()

                if self.game_state == "MENU":
                    if self.start_btn.is_clicked(pos):
                        self.start_new_game()



                elif self.game_state == "MAP":
                    if self.inventory_btn.is_clicked(pos):
                        self.game_state = "INVENTORY"
                    # ✅ Клик по ЛЮБОМУ активному узлу на карте
                    for i, node in enumerate(self.map_nodes):
                        if node.rect.collidepoint(pos) and node.active:
                            self.current_node_index = i
                            self.visit_location()
                            break

                elif self.game_state == "INVENTORY":
                    if self.map_btn.is_clicked(pos):
                        self.game_state = "MAP"
                    for i, armor in enumerate(self.inventory_armor):
                        if pygame.Rect(50 + i * 100, 600, 50, 50).collidepoint(pos):
                            self.equipped_armor = armor
                            self.message = f"Надета: {armor.name}"


                elif self.game_state == "PRE_BATTLE":
                    # Выбор карт из инвентаря
                    for card in self.inventory_cards:
                        if card.is_clicked(pos):
                            if card in self.battle_hand:
                                self.battle_hand.remove(card)
                            elif len(self.battle_hand) < 5:
                                self.battle_hand.append(card)
                    # Кнопка "В БОЙ!" — работает с ЛЮБЫМ количеством карт (0-5)
                    start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 60)
                    if start_btn_rect.collidepoint(pos):
                        self.start_battle()

                elif self.game_state == "BATTLE":
                    if self.turn == "PLAYER":
                        if self.current_enemy and self.current_enemy.dead:
                            continue

                        dice_clicked = False
                        for dice in self.dice_list:
                            if dice.is_clicked(pos) and not dice.used:
                                dice.selected = not dice.selected
                                dice_clicked = True
                                selected_count = len(self.get_selected_dice())
                                self.message = f"Выбрано кубиков: {selected_count}. Кликните на карту." if dice.selected else "Выберите кубик и карту."
                                self.message_timer = 60
                                break

                        if not dice_clicked:
                            for card in self.battle_hand:
                                if card.is_clicked(pos):
                                    if self.get_selected_dice():
                                        self.assign_dice_to_card(card)
                                    else:
                                        self.message = "Сначала выберите кубик!"
                                        self.message_timer = 60
                                    break

                        if self.end_turn_btn.is_clicked(pos):
                            self.end_player_turn()

                        if self.current_enemy and not self.current_enemy.dead:
                            enemy_rect = pygame.Rect(UI_POSITIONS['enemy_icon'][0], UI_POSITIONS['enemy_icon'][1], 120,
                                                     120)
                            if enemy_rect.collidepoint(pos):
                                self.enemy_info_visible = True
                                self.enemy_info_timer = 300
                                self.enemy_info_pos = (UI_POSITIONS['enemy_icon'][0] + 130,
                                                       UI_POSITIONS['enemy_icon'][1])

                elif self.game_state == "REWARD":

                    for i, card in enumerate(self.reward_cards):

                        if card.is_clicked(pos):
                            self.inventory_cards.append(card)

                            self.message = f"Получена карта: {card.name}!"

                            # После выбора карты — выбор события

                            self.generate_event_choice()

                elif self.game_state == "SHOP":
                    for i, card in enumerate(self.shop_cards):
                        if card.is_clicked(pos):
                            self.buy_card(i)
                            break

                    for i, card in enumerate(self.inventory_cards):
                        if card.is_clicked(pos):
                            if (self.last_click_pos and
                                    self.last_click_pos[0] - 5 <= pos[0] <= self.last_click_pos[0] + 5 and
                                    self.last_click_pos[1] - 5 <= pos[1] <= self.last_click_pos[1] + 5 and
                                    current_time - self.last_click_time < self.double_click_threshold):
                                if card.tier >= 4:
                                    self.message = "Карту 4 разряда нельзя продать!"
                                else:
                                    self.sell_card(i)
                            else:
                                if self.selected_upgrade_card == i:
                                    self.selected_upgrade_card = None
                                self.selected_upgrade_card = i
                                upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
                                self.message = f"Апгрейд за {upgrade_cost}G?"

                            self.last_click_time = current_time
                            self.last_click_pos = pos
                            break

                    if self.shop_buttons['next_floor'].is_clicked(pos) and self.selected_upgrade_card is None:
                        self.move_to_next_node()

                    if self.selected_upgrade_card is not None:
                        if self.shop_buttons['upgrade'].is_clicked(pos):
                            self.upgrade_card(self.selected_upgrade_card)
                        if self.shop_buttons['cancel'].is_clicked(pos):
                            self.selected_upgrade_card = None
                    # В блоках SHOP, TREASURE, CAMPFIRE:
                    next_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 60)
                    if next_btn_rect.collidepoint(pos):
                        # Переход к следующему бою
                        self.floor += 1
                        self.enter_battle_preparation()

                elif self.game_state == "EVENT_CHOICE":
                    # Выбор события
                    for i, event in enumerate(self.event_choices):
                        rect = pygame.Rect(200 + i * 270, 250, 250, 200)
                        if rect.collidepoint(pos):
                            if event["type"] == "shop":
                                self.game_state = "SHOP"
                                self.generate_shop_cards()
                            elif event["type"] == "treasure":
                                self.game_state = "TREASURE"
                                self.generate_treasure()
                            elif event["type"] == "campfire":
                                self.game_state = "CAMPFIRE"
                                self.heal_at_campfire()
                            break

                elif self.game_state == "TREASURE":
                    for i, item in enumerate(self.treasure_items):
                        rect = pygame.Rect(300 + i * 200, 200, 150, 150)
                        if rect.collidepoint(pos):
                            if item["type"] == "card":
                                self.inventory_cards.append(AbilityCard(*item["data"]))
                            elif item["type"] == "armor":
                                d = item["data"]
                                self.inventory_armor.append(
                                    Armor(d["name"], d["tier"], d["defense"], d["type"], d["asset"]))
                            self.move_to_next_node()
                    # В блоках SHOP, TREASURE, CAMPFIRE:
                    next_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 60)
                    if next_btn_rect.collidepoint(pos):
                        # Переход к следующему бою
                        self.floor += 1
                        self.enter_battle_preparation()

                elif self.game_state == "CAMPFIRE":
                    btn = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 60, "Дальше", GREEN)
                    if btn.is_clicked(pos):
                        self.move_to_next_node()
                    # В блоках SHOP, TREASURE, CAMPFIRE:
                    next_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 60)
                    if next_btn_rect.collidepoint(pos):
                        # Переход к следующему бою
                        self.floor += 1
                        self.enter_battle_preparation()

                elif self.game_state in ["GAME_OVER", "VICTORY"]:
                    if self.next_floor_btn.is_clicked(pos):
                        self.start_new_game()

                if self.game_state == "SHOP":
                    for btn in self.shop_buttons.values():
                        btn.check_hover(pygame.mouse.get_pos())
                elif self.game_state == "REWARD":
                    for card in self.reward_cards:
                        card.check_hover(pygame.mouse.get_pos())



            elif event.type == pygame.USEREVENT:

                # ✅ Обработка хода врага

                if self.game_state == "BATTLE" and self.turn == "ENEMY":
                    print(f"⏰ USEREVENT сработал! Ход врага")

                    self.enemy_turn()

                    # Сбрасываем таймер чтобы не срабатывал повторно

                    pygame.time.set_timer(pygame.USEREVENT, 0)

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.heal_flash_timer > 0:
            self.heal_flash_timer -= 1
        if self.hero_damage_flash_timer > 0:
            self.hero_damage_flash_timer -= 1
        if self.enemy_damage_flash_timer > 0:
            self.enemy_damage_flash_timer -= 1
        if self.upgrade_flash_timer > 0:
            self.upgrade_flash_timer -= 1
        if self.enemy_info_timer > 0:
            self.enemy_info_timer -= 1
            if self.enemy_info_timer <= 0:
                self.enemy_info_visible = False

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()