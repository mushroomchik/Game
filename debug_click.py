# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game

# Create game
game = Game()

# Simulate clicking on test_enemy_btn
print("Before click:")
print(f"  test_enemy_menu_visible: {game.test_enemy_menu_visible}")
print(f"  test_enemies count: {len(game.test_enemies)}")

# Get button position
btn = game.test_enemy_btn
pos = (btn.x + btn.width // 2, btn.y + btn.height // 2)
print(f"  Button position: {pos}")

# Simulate the click logic
if hasattr(game, 'test_enemy_btn') and game.test_enemy_btn.is_clicked(pos):
    print("  Button would be clicked!")
    game.test_enemy_menu_visible = not game.test_enemy_menu_visible
    game.test_enemy_scroll = 0
    print(f"  After click: test_enemy_menu_visible = {game.test_enemy_menu_visible}")

# Check if menu would be drawn
if game.test_enemy_menu_visible:
    print("  Menu should be drawn!")
    print(f"  test_enemies: {len(game.test_enemies)}")
    if game.test_enemies:
        print(f"  First enemy: {game.test_enemies[0]['name']}")
        print(f"  Last enemy: {game.test_enemies[-1]['name']}")
