"""События: награды, выбор"""
import random
from modules.config import (TIER_0_CARDS, TIER_1_CARDS, TIER_2_CARDS, TIER_4_CARDS, 
                            REWARD_CHANCES, SHOP_CARDS, ARMOR_TIERS,
                            TIER_DARK_T2_CARDS, TIER_DARK_T3_CARDS, TIER_DARK_T4_CARDS,
                            DEVIL_SHOP_TIER_CHANCES)
from modules.cards import AbilityCard
from modules.entities import Armor

class EventManager:
    @staticmethod
    def generate_reward_cards(is_boss: bool = False) -> list[AbilityCard]:
        """Генерация наградных карт"""
        cards = []
        if is_boss:
            available = list(TIER_4_CARDS)
            for _ in range(min(3, len(available))):
                data = random.choice(available)
                available.remove(data)
                cards.append(AbilityCard(*data))
        else:
            pool = [(c,0) for c in TIER_0_CARDS] + [(c,1) for c in TIER_1_CARDS] + [(c,2) for c in TIER_2_CARDS]
            weights = [REWARD_CHANCES[t] for _, t in pool]
            for _ in range(3):
                if not pool: break
                idx = random.choices(range(len(pool)), weights=weights)[0]
                cards.append(AbilityCard(*pool[idx][0]))
        return cards

    @staticmethod
    def generate_shop_cards() -> list[AbilityCard]:
        available = list(SHOP_CARDS)
        cards = []
        for _ in range(min(4, len(available))):
            data = random.choice(available)
            available.remove(data)
            cards.append(AbilityCard(*data))
        return cards

    @staticmethod
    def generate_devil_shop_cards() -> list[AbilityCard]:
        """Генерация карт для дьявольского магазина (3 карты)"""
        cards = []
        tiers = list(DEVIL_SHOP_TIER_CHANCES.keys())
        weights = list(DEVIL_SHOP_TIER_CHANCES.values())
        
        tier_dark_map = {
            2: TIER_DARK_T2_CARDS,
            3: TIER_DARK_T3_CARDS,
            4: TIER_DARK_T4_CARDS,
        }
        
        for _ in range(3):
            tier = random.choices(tiers, weights=weights)[0]
            available = list(tier_dark_map[tier])
            data = random.choice(available)
            cards.append(AbilityCard(*data))
        
        return cards

    @staticmethod
    def generate_treasure() -> list[dict]:
        """Генерация сокровищ — карта И броня"""
        items = []
        
        # Всегда добавляем карту
        data = random.choice(TIER_1_CARDS + TIER_2_CARDS)
        items.append({"type": "card", "data": data})
        
        # Всегда добавляем броню
        tier = random.choice([1, 2])
        armor_data = ARMOR_TIERS[tier]
        # Если это список (для тира 2), выбираем случайную броню
        if isinstance(armor_data, list):
            data = random.choice(armor_data).copy()
        else:
            data = armor_data.copy()
        data["tier"] = tier
        items.append({"type": "armor", "data": data})
        
        return items

    @staticmethod
    def get_event_choices() -> list[dict]:
        """Получение списка событий для выбора (обычный магазин или дьявольский)"""
        # 10% шанс на дьявольский магазин вместо обычного
        is_devil_shop = random.random() < 0.1
        
        if is_devil_shop:
            return [
                {"type": "devil_shop", "name": "Магазин", "icon": None},
                {"type": "treasure", "name": "Снаряжение", "icon": None},
                {"type": "campfire", "name": "Костер", "icon": None}
            ]
        else:
            return [
                {"type": "shop", "name": "Магазин", "icon": None},
                {"type": "treasure", "name": "Снаряжение", "icon": None},
                {"type": "campfire", "name": "Костер", "icon": None}
            ]