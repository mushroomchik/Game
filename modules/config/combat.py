"""Боевая система: типы урона и эффективность"""
# Типы урона
DAMAGE_TYPES = ["normal", "fire", "water", "electric", "grass", "ground"]

# Иконки типов
TYPE_ICONS = {
    "normal": "sword", "fire": "fire", "water": "shield",
    "electric": "crit", "grass": "heart", "ground": "shield"
}

# Названия для отображения
TYPE_NAMES = {
    "normal": "", "fire": "[Огонь] ", "water": "[Вода] ",
    "electric": "[Молния] ", "grass": "[Природа] ", "ground": "[Земля] "
}

# Эффективность: атакующий тип -> защищающийся тип -> множитель
# Огонь: вода x0.25, огонь x0.5, электричество x0.5, трава x2, земля x0.5
# Вода: вода x0.5, огонь x2, электричество x0.25, трава x0.5, земля x2
# Электричество: вода x2, огонь x0.5, электричество x0.5, трава x2, земля x0
# Трава: вода x2, огонь x0.25, электричество x0.25, трава x0.5, земля x2
# Земля: вода x0.25, огонь x2, электричество x2, трава x0.25, земля x0.5
TYPE_EFFECTIVENESS = {
    "normal": {"normal": 1.0, "fire": 1.0, "water": 1.0, "electric": 1.0, "grass": 1.0, "ground": 1.0, "spirit": 0.0, "elemental": 2.0},
    "fire": {"normal": 1.0, "fire": 0.5, "water": 0.25, "grass": 2.0, "ground": 0.5, "electric": 0.5, "spirit": 2.0, "elemental": 0.5},
    "water": {"normal": 1.0, "fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "electric": 0.25, "spirit": 2.0, "elemental": 0.5},
    "electric": {"normal": 1.0, "fire": 0.5, "water": 2.0, "grass": 2.0, "ground": 0.0, "electric": 0.5, "spirit": 2.0, "elemental": 0.5},
    "grass": {"normal": 1.0, "fire": 0.25, "water": 2.0, "grass": 0.5, "ground": 2.0, "electric": 0.25, "spirit": 2.0, "elemental": 0.5},
    "ground": {"normal": 1.0, "fire": 2.0, "water": 0.25, "grass": 0.25, "ground": 0.5, "electric": 2.0, "spirit": 2.0, "elemental": 0.5},
    "spirit": {"normal": 0.0, "fire": 2.0, "water": 2.0, "electric": 2.0, "grass": 2.0, "ground": 2.0, "spirit": 1.0, "elemental": 2.0},
    "elemental": {"normal": 0.25, "fire": 0.0, "water": 0.0, "electric": 0.0, "grass": 0.0, "ground": 0.0, "spirit": 0.0, "elemental": 1.0},
}