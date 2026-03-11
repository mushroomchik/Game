"""Система сохранений"""
import json
import os
from datetime import datetime
from modules.config import PLAYER_MAX_HP, DICE_COUNT

SAVE_DIR = "saves"
CURRENT_VERSION = "1.0"


def save_game(game, slot: int = 1) -> bool:
    """Сохранение состояния игры"""
    os.makedirs(SAVE_DIR, exist_ok=True)

    data = {
        "version": CURRENT_VERSION,
        "timestamp": datetime.now().isoformat(),
        "progress": {"floor": game.floor, "max_floor": game.max_floor, "total_wins": game.total_wins},
        "player": {
            "hp": game.player_hp, "max_hp": game.player_max_hp,
            "block": game.player_block, "gold": game.gold, "dice_count": game.dice_count,
        },
        "inventory": {
            "cards": [(c.name, c.tier, c.effect_type) for c in game.inventory_cards],
            "armor": game.equipped_armor.name if game.equipped_armor else None,
        },
        "map": {"current_node": game.current_node_index},
    }

    try:
        with open(f"{SAVE_DIR}/slot_{slot}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False


def load_game(slot: int = 1) -> dict | None:
    """Загрузка сохранения"""
    path = f"{SAVE_DIR}/slot_{slot}.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _migrate_save(data) if data.get("version") != CURRENT_VERSION else data
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None


def _migrate_save(data: dict) -> dict:
    """Миграция старых сохранений"""
    if "dice_count" not in data.get("player", {}):
        data["player"]["dice_count"] = DICE_COUNT
    if "max_hp" not in data.get("player", {}):
        data["player"]["max_hp"] = PLAYER_MAX_HP
    return data