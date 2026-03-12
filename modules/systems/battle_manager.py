"""Боевая система"""
from modules.config import TYPE_EFFECTIVENESS, TYPE_NAMES, ELEMENT_COLORS
from modules.cards import calculate_card_effect


class BattleManager:
    def __init__(self, player, enemy, dice_list, battle_hand, particles=None):
        self.player = player  # dict: hp, max_hp, block
        self.enemy = enemy
        self.dice_list = dice_list
        self.battle_hand = battle_hand
        self.particles = particles
        self.messages = []

    def activate_card(self, card) -> list[str]:
        """Активация карты"""
        messages = []
        effect = calculate_card_effect(card.effect_type, sum(card.assigned_dice),
                                       card.effect_value, card.description)
        attack_type = getattr(card, 'damage_type', 'normal')

        # Урон
        if "damage" in effect and effect["damage"] > 0 and self.enemy and not self.enemy.dead:
            final_dmg = self._calculate_damage(effect["damage"], attack_type)
            actual = self.enemy.take_damage(final_dmg, attack_type)
            if self.particles:
                self.particles.emit_damage(950, 30, attack_type)
            type_name = TYPE_NAMES.get(attack_type, "")
            messages.append(f"{type_name}{actual} урона")

        # Блок
        if "block" in effect and effect["block"] > 0:
            self.player['block'] += effect["block"]
            messages.append(f"+{effect['block']} блок")

        # Лечение
        if "heal" in effect and effect["heal"] > 0:
            healed = min(self.player['max_hp'] - self.player['hp'], effect["heal"])
            self.player['hp'] += healed
            if self.particles:
                self.particles.emit_heal(50, 20)
            messages.append(f"+{healed} HP")

        card.mark_used()
        return messages

    def _calculate_damage(self, base: int, attack_type: str) -> int:
        """Расчёт урона с учётом типов"""
        if not self.enemy: return base
        mult = self.enemy._get_effectiveness_multiplier(attack_type)
        return max(0, int(base * mult))

    def enemy_attack(self, armor=None) -> tuple[int, str]:
        """Атака врага"""
        if not self.enemy or self.enemy.dead: return 0, ""
        base_dmg, special = self.enemy.attack()
        
        # Применяем эффективность элемента урона врага через броню
        if armor and armor.armor_type == "elemental" and armor.element:
            # Если броня элементальная, урон проходит через её тип
            # Например: огненная броня vs водяной урон = x2 (вода эффективна против огня)
            # Ищем: атакующий тип (враг) vs защищающийся тип (броня)
            mult = TYPE_EFFECTIVENESS.get(self.enemy.damage_type, {}).get(armor.element, 1.0)
            dmg = int(base_dmg * mult)
            # Вычитаем защиту после применения множителя
            dmg = max(0, dmg - armor.defense)
        else:
            # Обычная броня - просто вычитаем защиту
            dmg = max(0, base_dmg - armor.defense) if armor else base_dmg
        
        # Блок игрока
        if self.player['block'] > 0:
            blocked = min(self.player['block'], dmg)
            self.player['block'] -= blocked
            dmg -= blocked
        # Применение урона
        if dmg > 0:
            self.player['hp'] = max(0, self.player['hp'] - dmg)
        return dmg, special