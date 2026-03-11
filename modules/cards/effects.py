"""Логика расчёта эффектов карт"""
# ✅ Используем dict вместо Dict (Python 3.9+)
from .registry import EFFECT_REGISTRY, register_effect

# === Базовые эффекты ===
def damage_effect(dice_sum: int, base: int) -> dict:
    return {"damage": dice_sum + base}

def heal_effect(dice_sum: int, base: int) -> dict:
    return {"heal": (dice_sum + base) // 2}

def block_effect(dice_sum: int, base: int) -> dict:
    return {"block": dice_sum + base}

def vampirism_effect(dice_sum: int, base: int) -> dict:
    dmg = dice_sum + base
    return {"damage": dmg, "heal": dmg // 2}

def omnipotent_effect(dice_sum: int, base: int) -> dict:
    dmg = dice_sum + base
    return {"damage": dmg, "heal": dmg // 3}

def special_effect(dice_sum: int, base: int, description: str = "") -> dict:
    """Special-эффект с парсингом описания"""
    desc = description.lower()
    if "блок" in desc or "защит" in desc:
        return {"damage": dice_sum + base, "block": base}
    elif "леч" in desc or "hp" in desc:
        return {"damage": dice_sum + base, "heal": base}
    return {"damage": dice_sum + base}

# Регистрация эффектов
for name, handler in [
    ("damage", damage_effect),
    ("heal", heal_effect),
    ("block", block_effect),
    ("vampirism", vampirism_effect),
    ("omnipotent", omnipotent_effect),
    ("special", special_effect),
]:
    register_effect(name, handler)

def calculate_card_effect(effect_type: str, dice_sum: int, base_value: int,
                         description: str = "") -> dict:  # ✅ dict вместо Dict[str, int]
    """Расчёт эффекта карты"""
    handler = EFFECT_REGISTRY.get(effect_type)
    if handler:
        # special требует описание
        if effect_type == "special":
            return handler(dice_sum, base_value, description)
        return handler(dice_sum, base_value)
    return {"damage": base_value}  # Дефолт