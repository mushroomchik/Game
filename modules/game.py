import pygame
import sys
import random
from modules.settings import *
from modules.utils import FONTS, IconRenderer
from modules.entities import Dice, Enemy, CharacterIcon
from modules.cards import AbilityCard
from modules.ui import HealthBar, Button


class Game:
    """Основной класс игры с типами элементов и этапами"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dicey Dungeons - Python Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # Прогресс
        self.floor = 1
        self.max_floor = MAX_FLOOR
        self.wins = 0
        self.total_wins = 0

        # Статы
        self.player_max_hp = PLAYER_MAX_HP
        self.player_hp = PLAYER_MAX_HP
        self.player_block = 0
        self.dice_count = DICE_COUNT
        self.gold = STARTING_GOLD

        # Инвентарь
        self.inventory = []
        self.turn_cards = []

        # Объекты
        self.dice_list = []
        self.current_enemy = None
        self.turn = "PLAYER"
        self.message = ""
        self.message_timer = 0
        self.game_state = "MENU"
        self.enemy_defeated_pending = False

        # Фазы: BATTLE, REWARD, SHOP
        self.phase = "BATTLE"

        # Награды
        self.reward_cards = []
        self.reward_hp_button = None

        # Магазин
        self.shop_cards = []
        self.selected_sell_card = None
        self.selected_upgrade_card = None

        # Отслеживание двойного клика
        self.last_click_time = 0
        self.last_click_pos = None
        self.double_click_threshold = 300

        # Иконка
        self.player_icon = None

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

    def setup_ui(self):
        self.player_health = HealthBar(UI_POSITIONS['hero_hp'][0], UI_POSITIONS['hero_hp'][1], 200, 30,
                                       self.player_max_hp, GREEN)
        self.enemy_health = None

        self.start_btn = Button(UI_POSITIONS['start_btn_center'] - 100, 380, 200, 60, "Начать игру", GREEN)
        self.next_floor_btn = Button(UI_POSITIONS['restart_btn_center'] - 100, 550, 200, 60, "Заново", GREEN)
        self.end_turn_btn = Button(UI_POSITIONS['end_turn_btn'][0], UI_POSITIONS['end_turn_btn'][1],
                                   UI_POSITIONS['end_turn_btn'][2], UI_POSITIONS['end_turn_btn'][3],
                                   "Завершить ход", BLUE)

        # DEBUG: Кнопка убийства врага (для разработчика)
        self.debug_kill_btn = Button(1050, 350, 140, 50, "🗡️ УБИТЬ", RED)
        self.debug_kill_btn.enabled = False

        self.shop_buttons = {
            'next_floor': Button(500, 720, 200, 50, "Следующий бой", GREEN),
            'sell': Button(300, 720, 150, 50, "Продать", ORANGE),
            'cancel': Button(450, 720, 150, 50, "Отмена", RED),
            'upgrade': Button(600, 720, 150, 50, "Апгрейд", BLUE),
        }

        self.dice_zone = pygame.Rect(*UI_POSITIONS['dice_zone'])
        self.card_zone = pygame.Rect(*UI_POSITIONS['card_zone'])

    def setup_player_icon(self):
        self.player_icon = CharacterIcon(UI_POSITIONS['hero_icon'][0], UI_POSITIONS['hero_icon'][1], 80,
                                         "assets/hero.png", "hero")

    def create_starting_inventory(self):
        self.inventory = []
        for card_data in STARTING_INVENTORY:
            card = AbilityCard(*card_data)
            self.inventory.append(card)

    def select_turn_cards(self):
        """5 случайных карт КАЖДЫЙ ход из инвентаря"""
        self.turn_cards = []

        if len(self.inventory) == 0:
            return

        available_indices = list(range(len(self.inventory)))
        random.shuffle(available_indices)

        for i in range(min(CARDS_PER_TURN, len(self.inventory))):
            if not available_indices:
                break
            idx = available_indices.pop()
            inv_card = self.inventory[idx]
            card = AbilityCard(
                inv_card.name,
                inv_card.description,
                inv_card.dice_requirement,
                inv_card.dice_cost,
                inv_card.effect_type,
                inv_card.effect_value,
                inv_card.color,
                inv_card.icon_type,
                inv_card.price,
                inv_card.tier,
                getattr(inv_card, 'damage_type', 'normal')
            )
            self.turn_cards.append(card)

    def get_stage_name(self, floor):
        """Получить название этапа по номеру этажа"""
        if floor <= 5:
            return "🌲 Лес"
        elif floor <= 10:
            return "🌊 Озеро"
        else:
            return "🔥 Пещера"

    def generate_reward_cards(self):
        """Генерация карт награды"""
        self.reward_cards = []
        is_boss = self.floor in BOSS_FLOORS

        if is_boss:
            # БОСС: только карты 4 тира
            available_cards = list(TIER_4_CARDS)
            for _ in range(3):
                if not available_cards:
                    break
                card_data = random.choice(available_cards)
                available_cards.remove(card_data)
                card = AbilityCard(*card_data)
                self.reward_cards.append(card)
            return

        # Обычный враг: карты 0-2 тира с весами
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
        """Магазин продаёт Разряд 1 и 2"""
        self.shop_cards = []
        available_cards = list(SHOP_CARDS)

        for _ in range(4):
            if not available_cards:
                break
            card_data = random.choice(available_cards)
            available_cards.remove(card_data)
            card = AbilityCard(*card_data)
            self.shop_cards.append(card)

    def check_dice_milestone(self):
        """Проверка прогрессии кубиков"""
        if self.total_wins in DICE_MILESTONES:
            self.dice_count += 1
            return True
        return False

    def is_boss_floor(self):
        """Проверка на босса"""
        return self.floor in BOSS_FLOORS

    def calculate_type_damage(self, attack_type, base_damage):
        """Расчёт урона с учётом типов"""
        if not self.current_enemy:
            return base_damage

        # Получаем тип врага (normal, fire, water, electric)
        enemy_element = getattr(self.current_enemy, 'damage_type', 'normal')
        enemy_type = getattr(self.current_enemy, 'enemy_type', 'normal')

        # Базовый множитель
        multiplier = TYPE_EFFECTIVENESS.get(attack_type, {}).get(enemy_element, 1.0)

        # Особые иммунитеты
        if enemy_type == "spirit":
            # Духи невосприимчивы к обычным атакам
            if attack_type == "normal":
                multiplier = 0
                self.message += " | 🚫 ИММУНИТЕТ!"
            else:
                multiplier *= 2  # Духи слабы к элементам
                self.message += " | 💥 ЭФФЕКТИВНО!"

        elif enemy_type == "elemental":
            # Элементали невосприимчивы к элементальным атакам
            if attack_type != "normal":
                multiplier = 0
                self.message += " | 🚫 ИММУНИТЕТ!"
            else:
                multiplier *= 2  # Элементали слабы к обычным атакам
                self.message += " | 💥 ЭФФЕКТИВНО!"

        final_damage = int(base_damage * multiplier)

        if multiplier > 1.0 and enemy_type not in ["spirit", "elemental"]:
            self.message += f" | ⚡ ЭФФЕКТИВНО! x{multiplier}"
        elif multiplier < 1.0 and multiplier > 0:
            self.message += f" | 🛡️ СЛАБО! x{multiplier}"
        elif multiplier == 0:
            pass  # Уже добавлено сообщение об иммунитете

        return max(0, final_damage)

    def create_enemy_for_floor(self, floor):
        """Создание врага с учётом этапа (региона)"""
        is_boss = floor in BOSS_FLOORS

        # Определяем этап
        if floor <= 5:
            stage = 1  # Лес
        elif floor <= 10:
            stage = 2  # Озеро
        else:
            stage = 3  # Пещера

        # Этап 1: ЛЕС (нормальные + трава)
        if stage == 1:
            normal_enemies = [
                (1, "Слайм", 25, (2, 4), "assets/slime.png", None, "slime", "normal", "grass"),
                (2, "Гоблин", 30, (3, 5), "assets/goblin.png", None, "goblin", "normal", "normal"),
                (3, "Волк", 35, (4, 6), "assets/wolf.png", None, "wolf", "normal", "normal"),
                (4, "Энт", 45, (5, 8), "assets/treant.png", None, "treant", "normal", "grass"),
                (5, "Лесной дух", 40, (4, 7), "assets/forest_spirit.png", None, "spirit", "spirit", "grass"),
            ]

        # Этап 2: ОЗЕРО (вода)
        elif stage == 2:
            normal_enemies = [
                (6, "Водяной слайм", 55, (5, 8), "assets/water_slime.png", None, "slime", "normal", "water"),
                (7, "Рыбочеловек", 60, (6, 9), "assets/fish_man.png", None, "fishman", "normal", "water"),
                (8, "Черепаха", 70, (5, 7), "assets/turtle.png", "block", "turtle", "normal", "water"),
                (9, "Водяной дух", 65, (6, 10), "assets/water_spirit.png", None, "spirit", "spirit", "water"),
                (10, "Нага", 75, (7, 11), "assets/naga.png", None, "naga", "normal", "water"),
            ]

        # Этап 3: ПЕЩЕРА (огонь + земля)
        else:
            normal_enemies = [
                (11, "Огненный слайм", 85, (7, 10), "assets/fire_slime.png", "fire", "slime", "normal", "fire"),
                (12, "Лавовый голем", 110, (8, 12), "assets/lava_golem.png", "fire", "golem", "elemental", "fire"),
                (13, "Огненный дух", 95, (8, 11), "assets/fire_spirit.png", "fire", "spirit", "spirit", "fire"),
                (14, "Каменный голем", 120, (9, 13), "assets/stone_golem.png", None, "golem", "elemental", "ground"),
                (15, "Огненный дракон", 130, (10, 15), "assets/fire_dragon.png", "fire", "dragon", "elemental", "fire"),
            ]

        if is_boss:
            boss_enemies = [
                # БОСС ЭТАПА 1 (Лес) - этаж 5
                ("ДРЕВНИЙ ДУХ", 120, (8, 12), "assets/forest_spirit.png", None, "spirit", "spirit", "normal"),
                # БОСС ЭТАПА 2 (Озеро) - этаж 10
                ("КРАКЕН", 180, (10, 15), "assets/kraken.png", None, "kraken", "elemental", "water"),
                # БОСС ЭТАПА 3 (Пещера) - этаж 15
                ("ПОВЕЛИТЕЛЬ ЛАВЫ", 250, (12, 18), "assets/lava_golem.png", "fire", "golem", "elemental", "fire"),
            ]
            boss_idx = (floor // 5 - 1) % len(boss_enemies)
            boss = boss_enemies[boss_idx]
            return Enemy(boss[0], boss[1], boss[2], boss[3], boss[4], boss[5], boss[6], boss[7])
        else:
            # ОБЫЧНЫЕ ВРАГИ ПО ЭТАПАМ
            if stage == 1:  # ЛЕС
                normal_enemies = [
                    (1, "Слайм", 25, (2, 4), "assets/slime.png", None, "slime", "normal", "normal"),
                    (2, "Гоблин", 30, (3, 5), "assets/goblin.png", None, "goblin", "normal", "normal"),
                    (3, "Волк", 35, (4, 6), "assets/wolf.png", None, "wolf", "normal", "normal"),
                    (4, "Энт", 45, (5, 8), "assets/treant.png", None, "treant", "normal", "normal"),
                    (5, "Лесной дух", 40, (4, 7), "assets/forest_spirit.png", None, "spirit", "spirit", "normal"),
                ]
            elif stage == 2:  # ОЗЕРО
                normal_enemies = [
                    (6, "Водяной слайм", 55, (5, 8), "assets/water_slime.png", None, "slime", "normal", "water"),
                    (7, "Рыбочеловек", 60, (6, 9), "assets/fish_man.png", None, "fishman", "normal", "water"),
                    (8, "Черепаха", 70, (5, 7), "assets/turtle.png", "block", "turtle", "normal", "water"),
                    (9, "Водяной дух", 65, (6, 10), "assets/water_spirit.png", None, "spirit", "spirit", "water"),
                    (10, "Нага", 75, (7, 11), "assets/naga.png", None, "naga", "normal", "water"),
                ]
            else:  # stage == 3: ПЕЩЕРА
                normal_enemies = [
                    (11, "Огненный слайм", 85, (7, 10), "assets/fire_slime.png", "fire", "slime", "normal", "fire"),
                    (12, "Лавовый голем", 110, (8, 12), "assets/lava_golem.png", "fire", "golem", "elemental", "fire"),
                    (13, "Огненный дух", 95, (8, 11), "assets/fire_spirit.png", "fire", "spirit", "spirit", "fire"),
                    (14, "Магмовый зверь", 120, (9, 13), "assets/magma_beast.png", "fire", "beast", "normal", "fire"),
                    (15, "Огненный дракон", 130, (10, 15), "assets/fire_dragon.png", "fire", "dragon", "elemental",
                     "fire"),
                ]

            # Выбираем врага на основе этажа
            enemy_idx = (floor - 1) % len(normal_enemies)
            enemy = normal_enemies[enemy_idx]
            return Enemy(enemy[1], enemy[2], enemy[3], enemy[4], enemy[5],
                         enemy[6], enemy[7], enemy[8])

    def reset_floor(self):
        self.player_block = 0
        self.player_health.update(self.player_hp, self.player_block)
        self.player_health.max_hp = self.player_max_hp
        self.current_enemy = self.create_enemy_for_floor(self.floor)
        self.enemy_health = HealthBar(UI_POSITIONS['enemy_hp'][0], UI_POSITIONS['enemy_hp'][1], 250, 30,
                                      self.current_enemy.max_hp, RED)
        self.enemy_health.update(self.current_enemy.hp, 0)
        self.phase = "BATTLE"
        self.select_turn_cards()
        self.roll_dice()
        self.turn = "PLAYER"
        self.enemy_defeated_pending = False

        stage_name = self.get_stage_name(self.floor)
        is_boss = self.is_boss_floor()
        if is_boss:
            self.message = f"{stage_name}, Этаж {self.floor}: 🏆 БОСС - {self.current_enemy.name}!"
        else:
            self.message = f"{stage_name}, Этаж {self.floor}: {self.current_enemy.name}!"
        self.message_timer = 180

    def start_new_game(self):
        self.floor = 1
        self.player_hp = PLAYER_MAX_HP
        self.player_max_hp = PLAYER_MAX_HP
        self.dice_count = DICE_COUNT
        self.gold = STARTING_GOLD
        self.wins = 0
        self.total_wins = 0
        self.phase = "BATTLE"
        self.reward_hp_button = None
        self.selected_upgrade_card = None
        self.heal_flash_timer = 0
        self.hero_damage_flash_timer = 0
        self.enemy_damage_flash_timer = 0
        self.upgrade_flash_timer = 0
        self.enemy_info_visible = False
        self.enemy_info_timer = 0
        self.create_starting_inventory()
        self.reset_floor()
        self.game_state = "PLAY"

    def next_floor(self):
        self.floor += 1
        self.wins += 1
        self.total_wins += 1
        self.message = f"Этаж {self.floor}!"
        if self.floor > self.max_floor:
            self.game_state = "VICTORY"
            self.message = "🏆 ВЫ ПРОШЛИ ВСЕ ЭТАЖИ!"
        else:
            self.reset_floor()

    def roll_dice(self):
        self.dice_list = []
        start_x = UI_POSITIONS['dice_zone'][0] + 25
        start_y = UI_POSITIONS['dice_zone'][1] + 20
        for i in range(self.dice_count):
            dice = Dice(start_x + i * 85, start_y)
            dice.roll()
            self.dice_list.append(dice)
        for card in self.turn_cards:
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

        if len(selected_dice) > card.dice_cost:
            self.message = f"Карта требует {card.dice_cost} кубика! Вы выбрали {len(selected_dice)}"
            self.message_timer = 60
            return False

        if len(selected_dice) < card.dice_cost:
            self.message = f"Нужно {card.dice_cost} кубика! Выберите ещё {card.dice_cost - len(selected_dice)}"
            self.message_timer = 60
            return False

        for dice in selected_dice:
            if not dice.can_be_used(card.dice_requirement):
                self.message = f"Нужен {card.get_requirement_text()}! (кубик {dice.value} не подходит)"
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

    def activate_card(self, card):
        """✅ ИСПРАВЛЕНО: С учётом типов урона"""
        effect = card.calculate_effect()
        if self.current_enemy is None or self.current_enemy.dead:
            return

        if card.effect_type == "damage":
            # ✅ Расчёт урона с типом
            attack_type = getattr(card, 'damage_type', 'normal')
            base_damage = effect
            self.message = f"{card.name}"
            calculated_dmg = self.calculate_type_damage(attack_type, base_damage)
            actual_dmg = self.current_enemy.take_damage(calculated_dmg)

            type_icons = {"normal": "⚔️", "fire": "🔥", "water": "💧", "electric": "⚡"}
            self.message = f"{type_icons.get(attack_type, '⚔️')} {card.name}: {actual_dmg} урона!"

            if self.enemy_health:
                self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
            self.enemy_damage_flash_timer = 10
            if self.current_enemy.dead:
                self.enemy_defeated()

        elif card.effect_type == "heal":
            self.player_hp = min(self.player_max_hp, self.player_hp + effect)
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            self.message = f"💚 {card.name}: +{effect} HP!"
            self.heal_flash_timer = 10

        elif card.effect_type == "block":
            self.player_block += effect
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            self.message = f"🛡️ {card.name}: +{effect} блок!"
            self.heal_flash_timer = 10

        elif card.effect_type == "vampirism":
            attack_type = getattr(card, 'damage_type', 'normal')
            base_damage = effect["damage"]
            self.message = f"{card.name}"
            calculated_dmg = self.calculate_type_damage(attack_type, base_damage)
            actual_dmg = self.current_enemy.take_damage(calculated_dmg)

            heal = effect["heal"]
            self.player_hp = min(self.player_max_hp, self.player_hp + heal)
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            if self.enemy_health:
                self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
            self.message = f"🩸 {card.name}: {actual_dmg} урона + {heal} HP!"
            self.heal_flash_timer = 10
            self.enemy_damage_flash_timer = 10
            if self.current_enemy.dead:
                self.enemy_defeated()

        elif card.effect_type == "omnipotent":
            attack_type = getattr(card, 'damage_type', 'normal')
            base_damage = effect["damage"]
            self.message = f"{card.name}"
            calculated_dmg = self.calculate_type_damage(attack_type, base_damage)
            actual_dmg = self.current_enemy.take_damage(calculated_dmg)

            heal = effect["heal"]
            self.player_hp = min(self.player_max_hp, self.player_hp + heal)
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            if self.enemy_health:
                self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
            self.message = f"✨ {card.name}: {actual_dmg} урона + {heal} HP!"
            self.heal_flash_timer = 10
            self.enemy_damage_flash_timer = 10
            if self.current_enemy.dead:
                self.enemy_defeated()

        elif card.effect_type == "special":
            dmg = effect["dice_sum"] + card.effect_value
            actual_dmg = self.current_enemy.take_damage(dmg)
            if self.enemy_health:
                self.enemy_health.update(self.current_enemy.hp, self.current_enemy.block)
            self.message = f"🎯 {card.name}: {actual_dmg} урона + эффект!"
            self.enemy_damage_flash_timer = 10
            if self.current_enemy.dead:
                self.enemy_defeated()

        card.mark_used()
        self.message_timer = 90

    def enemy_defeated(self):
        """✅ ИСПРАВЛЕНО: После босса тоже фаза REWARD с выбором карт"""
        self.message = f"{self.current_enemy.name} побеждён!"
        self.message_timer = 120
        self.enemy_defeated_pending = True

        is_boss = self.is_boss_floor()
        if is_boss:
            self.gold += GOLD_PER_BOSS
            self.message = f"🏆 БОСС побеждён! +{GOLD_PER_BOSS}G | Выбор легендарных карт!"
        else:
            self.gold += GOLD_PER_VICTORY
            self.message = f"Победа! +{GOLD_PER_VICTORY}G"

        bonus_dice = self.check_dice_milestone()
        if bonus_dice:
            self.message += " | +1 КУБИК!"

        if self.floor >= self.max_floor:
            self.game_state = "VICTORY"
        else:
            # ✅ И БОСС, и обычный враг → фаза REWARD
            self.phase = "REWARD"
            self.generate_reward_cards()
            pygame.time.set_timer(pygame.USEREVENT, 500)

    def select_reward_card(self, card_index):
        if 0 <= card_index < len(self.reward_cards):
            self.inventory.append(self.reward_cards[card_index])
            self.message = f"Получена карта: {self.reward_cards[card_index].name}!"
            self.phase = "SHOP"
            self.generate_shop_cards()

    def select_reward_hp(self):
        self.player_max_hp += 5
        self.player_hp = self.player_max_hp
        self.player_health.max_hp = self.player_max_hp
        self.player_health.update(self.player_hp, self.player_block)
        self.message = f"+5 Макс HP! ({self.player_max_hp}) и полное лечение!"
        self.phase = "SHOP"
        self.generate_shop_cards()

    def buy_card(self, card_index):
        if 0 <= card_index < len(self.shop_cards):
            card = self.shop_cards[card_index]
            if self.gold >= card.price:
                self.gold -= card.price
                self.inventory.append(card)
                self.message = f"Куплено: {card.name} за {card.price}G!"
                self.shop_cards.pop(card_index)
            else:
                self.message = "Недостаточно золота!"

    def sell_card(self, card_index):
        if 0 <= card_index < len(self.inventory):
            card = self.inventory[card_index]
            if card.tier >= 4:
                self.message = "Карту 4 разряда нельзя продать!"
                return
            sell_price = card.get_sell_price()
            self.gold += sell_price
            self.inventory.pop(card_index)
            self.message = f"Продано за {sell_price}G!"
            self.selected_sell_card = None
            self.selected_upgrade_card = None

    def upgrade_card(self, card_index):
        """Апгрейд карты до следующей версии"""
        if 0 <= card_index < len(self.inventory):
            card = self.inventory[card_index]

            # Проверка на максимальный тир
            if card.tier >= 3:
                self.message = "⚠️ Максимальный разряд!"
                self.selected_upgrade_card = None
                return

            upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)

            if self.gold >= upgrade_cost:
                # Ищем конкретный апгрейд
                upgrade_key = (card.name, card.tier)

                if upgrade_key in CARD_UPGRADES:
                    upgrade_name, upgrade_tier = CARD_UPGRADES[upgrade_key]

                    # Ищем карту апгрейда в TIER_3_CARDS
                    for card_data in TIER_3_CARDS:
                        if card_data[0] == upgrade_name and card_data[9] == upgrade_tier:
                            self.gold -= upgrade_cost
                            new_card = AbilityCard(*card_data)
                            self.inventory[card_index] = new_card
                            self.message = f"✨ Апгрейд: {card.name} → {upgrade_name}!"
                            self.upgrade_flash_timer = 30  # Визуальный эффект
                            self.selected_upgrade_card = None
                            return

                    self.message = "❌ Апгрейд не найден!"
                else:
                    self.message = "❌ Нет апгрейда для этой карты!"
            else:
                self.message = f"❌ Нужно {upgrade_cost}G для апгрейда!"

    def finish_shop(self):
        self.phase = "BATTLE"
        self.next_floor()

    def end_player_turn(self):
        if self.current_enemy and self.current_enemy.dead:
            return
        self.turn = "ENEMY"
        self.message = f"Ход {self.current_enemy.name}..."
        self.message_timer = 60
        pygame.time.set_timer(pygame.USEREVENT, 1500)

    def enemy_turn(self):
        if self.current_enemy.dead or self.enemy_defeated_pending:
            if self.floor >= self.max_floor:
                self.game_state = "VICTORY"
            else:
                self.phase = "REWARD"
                self.generate_reward_cards()
            return

        dmg, special = self.current_enemy.attack()
        if self.player_block > 0:
            blocked = min(self.player_block, dmg)
            self.player_block -= blocked
            dmg -= blocked
            self.message = f"Блок: -{blocked} "
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
        if dmg > 0:
            self.player_hp -= dmg
            self.player_health.update(self.player_hp, self.player_block)
            self.player_health.max_hp = self.player_max_hp
            self.message += f"{dmg} урона! {special}"
            self.hero_damage_flash_timer = 10

        self.check_player_death()
        if self.player_hp > 0:
            self.turn = "PLAYER"
            self.roll_dice()
            self.select_turn_cards()
            self.message = "Клик: кубик → карта"
        self.message_timer = 120

    def check_player_death(self):
        if self.player_hp <= 0:
            self.game_state = "GAME_OVER"
            self.message = f"Погибли на этаже {self.floor}!"

    def draw_menu(self):
        self.screen.fill(DARK_BLUE)
        title = FONTS['large'].render("Dicey Dungeons", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        subtitle = FONTS['medium'].render("Python Edition", True, LIGHT_GRAY)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
        self.start_btn.draw(self.screen)

        instructions = [
            "Как играть:",
            "1. Кликните на кубик (выделится)",
            "2. Кликните на карту способности",
            "3. После победы: +5 HP или новая карта",
            "4. В магазине: купите, продайте или улучшите карты",
            "5. Используйте стихии против врагов!",
            "6. Клик по врагу = информация о нём",
        ]
        for i, line in enumerate(instructions):
            text = FONTS['small'].render(line, True, LIGHT_GRAY)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 480 + i * 32))

    def draw_game(self):
        self.screen.fill(DARK_GRAY)

        floor_text = FONTS['medium'].render(f"Этаж {self.floor}/{self.max_floor}", True, GOLD)
        self.screen.blit(floor_text, (SCREEN_WIDTH // 2 - floor_text.get_width() // 2, 10))

        self.player_icon.draw(self.screen)
        player_text = FONTS['small'].render("Герой", True, GREEN)
        self.screen.blit(player_text, (UI_POSITIONS['hero_name'][0], UI_POSITIONS['hero_name'][1]))

        # Эффект лечения (зелёная рамка)
        if self.heal_flash_timer > 0:
            pygame.draw.rect(self.screen, GREEN,
                             (self.player_health.x - 3, self.player_health.y - 3,
                              self.player_health.width + 6, self.player_health.height + 6),
                             3, border_radius=7)

        # Эффект урона по ГЕРОЮ (красная рамка вокруг иконки)
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
            f"Кубиков: {self.dice_count} | Карт: {len(self.inventory)} | Победы: {self.total_wins}", True, LIGHT_GRAY)
        self.screen.blit(dice_text, (140, 115))

        if self.phase == "REWARD":
            self.draw_reward_screen()
        elif self.phase == "SHOP":
            self.draw_shop()
        else:
            self.draw_battle()

    def draw_battle(self):
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
        for i, card in enumerate(self.turn_cards[:5]):
            card.set_position(card_start_x + i * card_spacing, self.card_zone.y + 10)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen)

        self.end_turn_btn.draw(self.screen)

        # DEBUG: Кнопка убийства врага
        if self.phase == "BATTLE" and self.turn == "PLAYER":
            self.debug_kill_btn.enabled = True
            self.debug_kill_btn.draw(self.screen)
        else:
            self.debug_kill_btn.enabled = False

        turn_text = FONTS['medium'].render(f"{'ВАШ ХОД' if self.turn == 'PLAYER' else 'ХОД ВРАГА'}",
                                           True, YELLOW if self.turn == "PLAYER" else RED)
        self.screen.blit(turn_text, (UI_POSITIONS['turn_text'][0], UI_POSITIONS['turn_text'][1]))

        if self.current_enemy:
            # Эффект урона по ВРАГУ (красная рамка)
            if self.enemy_damage_flash_timer > 0:
                enemy_rect = pygame.Rect(UI_POSITIONS['enemy_icon'][0] - 5,
                                         UI_POSITIONS['enemy_icon'][1] - 5,
                                         130, 130)
                pygame.draw.rect(self.screen, RED, enemy_rect, 6, border_radius=15)

            self.enemy_health.draw(self.screen)
            self.current_enemy.draw(self.screen, UI_POSITIONS['enemy_icon'][0], UI_POSITIONS['enemy_icon'][1])

            # Информация о враге при клике
            if self.enemy_info_visible and self.enemy_info_timer > 0:
                self.draw_enemy_info()

    def draw_enemy_info(self):
        """Отрисовка информации о враге"""
        if not self.current_enemy:
            return

        info_lines = self.current_enemy.get_info_text()

        # Рассчитываем размер окна
        max_width = 0
        for line in info_lines:
            text_width = FONTS['tiny'].render(line, True, WHITE).get_width()
            if text_width > max_width:
                max_width = text_width

        box_width = max_width + 20
        box_height = len(info_lines) * 18 + 10

        # Позиция (чтобы не выходило за экран)
        info_x = min(self.enemy_info_pos[0], SCREEN_WIDTH - box_width - 10)
        info_y = min(self.enemy_info_pos[1], SCREEN_HEIGHT - box_height - 10)

        # Фон окна
        pygame.draw.rect(self.screen, DARK_BLUE, (info_x, info_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(self.screen, GOLD, (info_x, info_y, box_width, box_height), 2, border_radius=8)

        # Текст
        for i, line in enumerate(info_lines):
            # Цвет для важных строк
            if "Иммунитет" in line or "Слаб" in line or "x2" in line or "x0" in line:
                color = GOLD
            elif "Тип:" in line or "HP:" in line or "Урон:" in line:
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

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        self.reward_hp_button = Button(button_x, 150, button_width, button_height, "+5 Макс HP + Лечение", GREEN)
        self.reward_hp_button.draw(self.screen)

        subtitle = FONTS['medium'].render("ИЛИ выберите карту:", True, LIGHT_GRAY)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        for i, card in enumerate(self.reward_cards):
            card.set_position(180 + i * 270, 280)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen)

        info_text = FONTS['small'].render(
            f"Кубиков: {self.dice_count} | Карт: {len(self.inventory)} | Победы: {self.total_wins}", True, LIGHT_GRAY)
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
        for i, card in enumerate(self.inventory):
            row = i // cards_per_row
            col = i % cards_per_row
            card.set_position(start_x + col * 155, start_y + row * 200)
            card.check_hover(pygame.mouse.get_pos())
            card.draw(self.screen, show_price=True, price_type="sell", player_gold=self.gold)

            if self.selected_upgrade_card == i:
                pygame.draw.rect(self.screen, BLUE, (card.x - 3, card.y - 3,
                                                     card.width + 6, card.height + 6), 3, border_radius=12)

        # Визуальный эффект успешного апгрейда
        if hasattr(self, 'upgrade_flash_timer') and self.upgrade_flash_timer > 0:
            pygame.draw.rect(self.screen, GOLD,
                             (150 - 5, 460 - 5,
                              6 * 155 + 10,
                              max(200, (len(self.inventory) // 6 + 1) * 200 + 10)),
                             4, border_radius=15)

        if self.selected_upgrade_card is not None:
            card = self.inventory[self.selected_upgrade_card]
            upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
            next_tier = card.tier + 1
            upgrade_color = GREEN if self.gold >= upgrade_cost else RED

            upgrade_key = (card.name, card.tier)
            if upgrade_key in CARD_UPGRADES:
                upgrade_name = CARD_UPGRADES[upgrade_key][0]
                upgrade_info = FONTS['small'].render(f"→ {upgrade_name} за ", True, WHITE)
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
                elif self.game_state == "PLAY":
                    if self.phase == "REWARD":
                        if self.reward_hp_button and self.reward_hp_button.is_clicked(pos):
                            self.select_reward_hp()
                        for i, card in enumerate(self.reward_cards):
                            if card.is_clicked(pos):
                                self.select_reward_card(i)
                                break
                    elif self.phase == "SHOP":
                        for i, card in enumerate(self.shop_cards):
                            if card.is_clicked(pos):
                                self.buy_card(i)
                                break

                        for i, card in enumerate(self.inventory):
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
                                    if self.selected_sell_card == i:
                                        self.selected_sell_card = None
                                    self.selected_upgrade_card = i
                                    upgrade_cost = UPGRADE_COSTS.get(card.tier, 999)
                                    self.message = f"Апгрейд за {upgrade_cost}G?"

                                self.last_click_time = current_time
                                self.last_click_pos = pos
                                break

                        if self.shop_buttons['next_floor'].is_clicked(pos) and self.selected_upgrade_card is None:
                            self.finish_shop()

                        if self.selected_upgrade_card is not None:
                            if self.shop_buttons['upgrade'].is_clicked(pos):
                                self.upgrade_card(self.selected_upgrade_card)
                            if self.shop_buttons['cancel'].is_clicked(pos):
                                self.selected_upgrade_card = None
                    else:
                        if self.turn == "PLAYER":
                            if self.current_enemy and self.current_enemy.dead:
                                continue

                            # ✅ DEBUG: Кнопка убийства врага
                            if self.debug_kill_btn.is_clicked(pos) and self.debug_kill_btn.enabled:
                                self.current_enemy.hp = 0
                                self.current_enemy.dead = True
                                self.enemy_health.update(0, 0)
                                self.message = "🧪 DEBUG: Враг убит!"
                                self.message_timer = 60
                                self.enemy_defeated()
                                continue

                            # ✅ Клик по врагу → показать информацию
                            if self.current_enemy and not self.current_enemy.dead:
                                enemy_rect = pygame.Rect(
                                    UI_POSITIONS['enemy_icon'][0],
                                    UI_POSITIONS['enemy_icon'][1],
                                    120, 120
                                )
                                if enemy_rect.collidepoint(pos):
                                    self.enemy_info_visible = True
                                    self.enemy_info_timer = 300  # 5 секунд
                                    self.enemy_info_pos = (
                                        UI_POSITIONS['enemy_icon'][0] + 130,
                                        UI_POSITIONS['enemy_icon'][1]
                                    )
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
                                for card in self.turn_cards:
                                    if card.is_clicked(pos):
                                        if self.get_selected_dice():
                                            self.assign_dice_to_card(card)
                                        else:
                                            self.message = "Сначала выберите кубик!"
                                            self.message_timer = 60
                                        break
                            if self.end_turn_btn.is_clicked(pos):
                                self.end_player_turn()
                elif self.game_state in ["GAME_OVER", "VICTORY"]:
                    if self.next_floor_btn.is_clicked(pos):
                        self.start_new_game()
            elif event.type == pygame.USEREVENT:
                if self.turn == "ENEMY" and self.game_state == "PLAY":
                    self.enemy_turn()
                elif self.enemy_defeated_pending and self.game_state == "PLAY":
                    if self.floor >= self.max_floor:
                        self.game_state = "VICTORY"
                    self.enemy_defeated_pending = False
                pygame.time.set_timer(pygame.USEREVENT, 0)

        if self.game_state == "MENU":
            self.start_btn.check_hover(pygame.mouse.get_pos())
        elif self.game_state == "PLAY":
            if self.phase == "BATTLE":
                self.end_turn_btn.check_hover(pygame.mouse.get_pos())
                self.debug_kill_btn.check_hover(pygame.mouse.get_pos())
            elif self.phase == "SHOP":
                for btn in self.shop_buttons.values():
                    btn.check_hover(pygame.mouse.get_pos())
            elif self.phase == "REWARD":
                if self.reward_hp_button:
                    self.reward_hp_button.check_hover(pygame.mouse.get_pos())
                for card in self.reward_cards:
                    card.check_hover(pygame.mouse.get_pos())
        elif self.game_state in ["GAME_OVER", "VICTORY"]:
            self.next_floor_btn.check_hover(pygame.mouse.get_pos())

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

    def draw(self):
        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "PLAY":
            self.draw_game()
        elif self.game_state == "GAME_OVER":
            self.draw_game()
            self.draw_game_over()
        elif self.game_state == "VICTORY":
            self.draw_game()
            self.draw_victory()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()