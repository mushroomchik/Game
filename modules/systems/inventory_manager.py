"""Инвентарь, магазин, апгрейды"""
from modules.config import UPGRADE_COSTS, SELL_PRICE_MULTIPLIER, CARD_UPGRADES, TIER_3_CARDS
from modules.cards import AbilityCard

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