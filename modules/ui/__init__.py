"""UI компоненты"""
from .components import HealthBar, Button, Tooltip
from .renderer import GameRenderer  # ✅ Импортируем класс

__all__ = ['HealthBar', 'Button', 'Tooltip', 'GameRenderer']