# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game

game = Game()
game._reset_game()

print("test_enemies list:")
for i, e in enumerate(game.test_enemies):
    print(f"  {i}: {e['name']} (HP:{e['hp']}, dmg:{e['dmg']}, icon:{e['icon']})")
