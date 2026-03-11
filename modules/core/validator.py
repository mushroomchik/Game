"""Валидация игровых данных при старте"""
from modules.config import (
    TIER_0_CARDS, TIER_1_CARDS, TIER_2_CARDS, TIER_3_CARDS,
    CARD_UPGRADES, STARTING_INVENTORY, TYPE_ICONS
)
from modules.utils.icons import VALID_ICONS


def validate_game_data() -> list[str]:
    """Возвращает список ошибок (пустой = всё ок)"""
    errors = []

    # 1. Проверка длины кортежей карт (должно быть 11 элементов)
    for source_name, card_list in [
        ("TIER_0", TIER_0_CARDS), ("TIER_1", TIER_1_CARDS),
        ("TIER_2", TIER_2_CARDS), ("TIER_3", TIER_3_CARDS),
        ("STARTING", STARTING_INVENTORY),
    ]:
        for i, card_data in enumerate(card_list):
            if len(card_data) != 11:
                errors.append(f"{source_name} карта #{i}: ожидается 11 полей, получено {len(card_data)}")

    # 2. Проверка апгрейдов
    all_tier_cards = {
        0: TIER_0_CARDS, 1: TIER_1_CARDS, 2: TIER_2_CARDS, 3: TIER_3_CARDS,
    }
    for (name, tier), (upgrade_name, upgrade_tier) in CARD_UPGRADES.items():
        target_list = all_tier_cards.get(upgrade_tier)
        if not target_list or not any(c[0] == upgrade_name for c in target_list):
            errors.append(f"Апгрейд {name}(T{tier}) → {upgrade_name}(T{upgrade_tier}): целевая карта не найдена")

    # 3. Проверка иконок
    for icon_type in TYPE_ICONS.values():
        if icon_type not in VALID_ICONS:
            errors.append(f"Неизвестная иконка в TYPE_ICONS: {icon_type}")

    return errors