"""Инвентарь, магазин, апгрейды"""
from modules.config import UPGRADE_COSTS, SELL_PRICE_MULTIPLIER, CARD_UPGRADES, TIER_3_CARDS, ARMOR_UPGRADES
from modules.cards import AbilityCard
from modules.entities import Armor

class InventoryManager:
    def __init__(self):
        self.cards = []
        self.armor = []
        self.equipped_armor = None
        self.gold = 0
        self.selected_cards = []  # Карты выбранные для боя

    def add_card(self, card: AbilityCard):
        self.cards.append(card)

    def remove_card(self, index: int) -> AbilityCard | None:
        if 0 <= index < len(self.cards):
            return self.cards.pop(index)
        return None

    def sell_card(self, index: int) -> int:
        card = self.cards[index] if 0 <= index < len(self.cards) else None
        if not card or card.tier >= 4: return 0
        price = max(1, int(card.price * SELL_PRICE_MULTIPLIER))
        self.remove_card(index)
        self.gold += price
        return price

    def upgrade_card(self, index: int) -> tuple[bool, str]:
        if not (0 <= index < len(self.cards)):
            return False, "Карта не найдена"
        card = self.cards[index]
        if card.tier >= 3:
            return False, "Максимальный разряд!"
        cost = UPGRADE_COSTS.get(card.tier, 999)
        if self.gold < cost:
            return False, f"Нужно {cost}G"
        key = (card.name, card.tier)
        if key not in CARD_UPGRADES:
            return False, "Нет апгрейда"
        upgrade_name, upgrade_tier = CARD_UPGRADES[key]
        target = next((c for c in TIER_3_CARDS if c[0]==upgrade_name and c[9]==upgrade_tier), None)
        if not target:
            return False, "Апгрейд не найден"
        self.gold -= cost
        self.cards[index] = AbilityCard(*target)
        return True, f"Апгрейд: {card.name} → {upgrade_name}!"

    def equip_armor(self, armor):
        self.equipped_armor = armor

    def get_battle_hand(self, max_cards: int = 5) -> list:
        # Используем выбранные карты или все доступные (до 5)
        if self.selected_cards:
            return self.selected_cards[:max_cards]
        return self.cards[:max_cards]

    def craft_armor(self, armor_name: str, armor_tier: int) -> tuple[bool, str]:
        """Объединение 3 одинаковых броней в улучшенную версию"""
        
        # Специальный рецепт: Броня тьмы из Огненная+ + Водяная+ + Земляная+
        if armor_name == "Броня тьмы" and armor_tier == 5:
            required = ["Огненная броня+", "Водяная броня+", "Земляная броня+"]
            found = []
            for req_name in required:
                for a in self.armor:
                    if a.name == req_name and a.tier == 3:
                        found.append(req_name)
                        break
            
            if len(found) < 3:
                return False, "Нужно: Огненная+, Водяная+, Земляная+"
            
            # Удаляем эти 3 брони
            new_armor_list = []
            removed = set()
            for a in self.armor:
                if a.name in required and a.name not in removed:
                    removed.add(a.name)
                    continue
                new_armor_list.append(a)
            self.armor = new_armor_list
            
            # Добавляем броню тьмы
            new_armor = Armor("Броня тьмы", 5, 8, "elemental", "armor_dark_5.png", "dark")
            self.armor.append(new_armor)
            
            # Если экипирована была одна из удаленных - экипируем новую
            if self.equipped_armor and self.equipped_armor.name in required:
                self.equipped_armor = new_armor
            
            return True, "Создано: Броня тьмы!"
        
        # Обычный крафт - ищем 3 одинаковые брони
        matching_armor = [a for a in self.armor if a.name == armor_name and a.tier == armor_tier]
        
        if len(matching_armor) < 3:
            return False, "Нужно 3 одинаковые брони"
        
        upgrade_key = (armor_name, armor_tier)
        if upgrade_key not in ARMOR_UPGRADES:
            return False, "Нет рецепта для этой брони"
        
        upgrade_info = ARMOR_UPGRADES[upgrade_key]
        upgrade_name, upgrade_tier, upgrade_defense, upgrade_type, upgrade_element, upgrade_asset = upgrade_info
        
        # Удаляем 3 брони
        removed_count = 0
        new_armor_list = []
        for a in self.armor:
            if a.name == armor_name and a.tier == armor_tier and removed_count < 3:
                removed_count += 1
                continue
            new_armor_list.append(a)
        self.armor = new_armor_list
        
        # Добавляем новую броню
        new_armor = Armor(upgrade_name, upgrade_tier, upgrade_defense, upgrade_type, upgrade_asset, upgrade_element)
        self.armor.append(new_armor)
        
        # Если экипирована была одна из удаленных - экипируем новую
        if self.equipped_armor and self.equipped_armor.name == armor_name and self.equipped_armor.tier == armor_tier:
            self.equipped_armor = new_armor
        
        return True, f"Создано: {upgrade_name}!"