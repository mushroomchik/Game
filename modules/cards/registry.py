"""Реестр эффектов для расширяемости"""
# ✅ Используем dict вместо Dict (Python 3.9+)

# Тип функции-обработчика эффекта
EffectHandler = callable  # Упрощённо, или используйте typing.Callable если нужно

EFFECT_REGISTRY: dict = {}  # ✅ dict вместо Dict[str, EffectHandler]

def register_effect(name: str, handler):
    """Регистрация нового типа эффекта"""
    EFFECT_REGISTRY[name] = handler

def get_effect(name: str):
    """Получение обработчика эффекта"""
    return EFFECT_REGISTRY.get(name)