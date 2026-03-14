"""Боевая система: типы урона и эффективность"""
# Типы урона
DAMAGE_TYPES = ["normal", "fire", "water", "electric", "grass", "ground", "light", "dark"]

# Иконки типов
TYPE_ICONS = {
    "normal": "sword", "fire": "fire", "water": "shield",
    "electric": "crit", "grass": "heart", "ground": "shield",
    "light": "star", "dark": "crit"
}

# Названия для отображения
TYPE_NAMES = {
    "normal": "", "fire": "[Огонь] ", "water": "[Вода] ",
    "electric": "[Молния] ", "grass": "[Природа] ", "ground": "[Земля] ",
    "light": "[Свет] ", "dark": "[Тьма] "
}

# Эффективность: атакующий тип -> защищающийся тип -> множитель
# Огонь: вода x0.25, огонь x0.5, электричество x0.5, трава x2, земля x0.5, свет x1, тьма x0.5
# Вода: вода x0.5, огонь x2, электричество x0.25, трава x0.5, земля x2, свет x1, тьма x0.5
# Электричество: вода x2, огонь x0.5, электричество x0.5, трава x2, земля x0, свет x1, тьма x0.5
# Трава: вода x2, огонь x0.25, электричество x0.25, трава x0.5, земля x2, свет x1, тьма x0.5
# Земля: вода x0.25, огонь x2, электричество x2, трава x0.25, земля x0.5, свет x1, тьма x0.5
# Свет: x1 по всем, x2 по тьме
# Тьма: x2 по всем, x0.5 по свету
TYPE_EFFECTIVENESS = {
    "normal": {"normal": 1.0, "fire": 1.0, "water": 1.0, "electric": 1.0, "grass": 1.0, "ground": 1.0, "light": 1.0, "dark": 1.0, "spirit": 0.0, "elemental": 2.0},
    "fire": {"normal": 1.0, "fire": 0.5, "water": 0.25, "grass": 2.0, "ground": 0.5, "electric": 0.5, "light": 1.0, "dark": 0.5, "spirit": 2.0, "elemental": 0.5},
    "water": {"normal": 1.0, "fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "electric": 0.25, "light": 1.0, "dark": 0.5, "spirit": 2.0, "elemental": 0.5},
    "electric": {"normal": 1.0, "fire": 0.5, "water": 2.0, "grass": 2.0, "ground": 0.0, "electric": 0.5, "light": 1.0, "dark": 0.5, "spirit": 2.0, "elemental": 0.5},
    "grass": {"normal": 1.0, "fire": 0.25, "water": 2.0, "grass": 0.5, "ground": 2.0, "electric": 0.25, "light": 1.0, "dark": 0.5, "spirit": 2.0, "elemental": 0.5},
    "ground": {"normal": 1.0, "fire": 2.0, "water": 0.25, "grass": 0.25, "ground": 0.5, "electric": 2.0, "light": 1.0, "dark": 0.5, "spirit": 2.0, "elemental": 0.5},
    # Свет: x1 по всем, x2 по тьме
    "light": {"normal": 1.0, "fire": 1.0, "water": 1.0, "electric": 1.0, "grass": 1.0, "ground": 1.0, "light": 1.0, "dark": 2.0, "spirit": 1.0, "elemental": 1.0},
    # Тьма: x2 по всем, x0.5 по свету
    "dark": {"normal": 2.0, "fire": 2.0, "water": 2.0, "electric": 2.0, "grass": 2.0, "ground": 2.0, "light": 0.5, "dark": 1.0, "spirit": 2.0, "elemental": 2.0},
    # Духи уязвимы к свету и тьме (x1, как к обычным элементам)
    "spirit": {"normal": 0.0, "fire": 2.0, "water": 2.0, "electric": 2.0, "grass": 2.0, "ground": 2.0, "light": 1.0, "dark": 1.0, "spirit": 1.0, "elemental": 2.0},
    "elemental": {"normal": 0.25, "fire": 0.0, "water": 0.0, "electric": 0.0, "grass": 0.0, "ground": 0.0, "light": 0.5, "dark": 0.5, "spirit": 0.0, "elemental": 1.0},
}