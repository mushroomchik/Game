# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game

# Create game - starts in MENU state
game = Game()
print("1. After init:")
print(f"   game_state: {game.game_state}")
print(f"   test_enemies: {len(game.test_enemies)}")

# Simulate clicking "Start game" button
# Start button is at center, y=380
start_btn = game.start_btn
pos = (start_btn.rect.x + start_btn.rect.width // 2, start_btn.rect.y + start_btn.rect.height // 2)
print(f"\n2. Clicking start button at {pos}")

# This would call _reset_game()
# Let's call it manually
game._reset_game()

print(f"\n3. After _reset_game:")
print(f"   game_state: {game.game_state}")
print(f"   test_enemies: {len(game.test_enemies)}")
print(f"   test_enemy_menu_visible: {game.test_enemy_menu_visible}")

# Now click on test_enemy_btn
btn = game.test_enemy_btn
pos = (btn.rect.x + btn.rect.width // 2, btn.rect.y + btn.rect.height // 2)
print(f"\n4. Clicking test_enemy_btn at {pos}")
print(f"   Button rect: {btn.rect}")

if btn.is_clicked(pos):
    print("   Button IS clicked!")
    game.test_enemy_menu_visible = not game.test_enemy_menu_visible
    game.test_enemy_scroll = 0
    print(f"   After click: test_enemy_menu_visible = {game.test_enemy_menu_visible}")
else:
    print("   Button NOT clicked!")

# Now check if menu would be drawn
if game.test_enemy_menu_visible:
    print("\n5. Menu should be drawn!")
    print(f"   test_enemies count: {len(game.test_enemies)}")
    for i, e in enumerate(game.test_enemies[:5]):
        print(f"   {i}: {e['name']}")
