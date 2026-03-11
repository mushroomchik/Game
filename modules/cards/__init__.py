"""Система карт"""
from .card import AbilityCard
from .effects import calculate_card_effect, EFFECT_REGISTRY
from .registry import register_effect

__all__ = ['AbilityCard', 'calculate_card_effect', 'EFFECT_REGISTRY', 'register_effect']