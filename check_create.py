# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game
from modules.config import LOCATIONS

game = Game()

# Check what enemy _create_enemy creates for floor 1
enemy = game._create_enemy(1)
print(f"_create_enemy(1) returns: {enemy.name}")
print(f"  HP: {enemy.hp}")
print(f"  Damage: {enemy.damage_range}")

# Check what the first enemy in LOCATIONS is
print("\nFirst enemy in LOCATIONS:")
loc = LOCATIONS['forest']
print(f"  {loc['enemies'][0]}")
print(f"  Boss: {loc['boss']}")