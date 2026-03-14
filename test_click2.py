# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game
from modules.config import SCREEN_WIDTH

game = Game()
game._reset_game()

print("Testing button clicks...")
print(f"SCREEN_WIDTH = {SCREEN_WIDTH}")

# Get button positions
test_enemy_btn = game.test_enemy_btn
cheat_btn = game.cheat_btn
fight_from_map_btn = game.fight_from_map_btn

print(f"\ntest_enemy_btn rect: {test_enemy_btn.rect}")
print(f"cheat_btn rect: {cheat_btn.rect}")
print(f"fight_from_map_btn rect: {fight_from_map_btn.rect}")

# Test clicking on test_enemy_btn
# Click in the center of the button
test_pos = (test_enemy_btn.rect.centerx, test_enemy_btn.rect.centery)
print(f"\nClicking test_enemy_btn at {test_pos}")

# Check what buttons would be clicked
print(f"test_enemy_btn.is_clicked: {test_enemy_btn.is_clicked(test_pos)}")
print(f"cheat_btn.is_clicked: {cheat_btn.is_clicked(test_pos)}")
print(f"fight_from_map_btn.is_clicked: {fight_from_map_btn.is_clicked(test_pos)}")

# Now simulate the full click
print("\n--- Simulating full click ---")
print(f"Before: test_enemy_menu_visible = {game.test_enemy_menu_visible}")

# The click logic
if test_enemy_btn.is_clicked(test_pos):
    game.test_enemy_menu_visible = not game.test_enemy_menu_visible
    game.test_enemy_scroll = 0
    print(f"After toggle: test_enemy_menu_visible = {game.test_enemy_menu_visible}")
elif cheat_btn.is_clicked(test_pos):
    game.cheat_menu_visible = not game.cheat_menu_visible
    print(f"cheat_btn was clicked!")

# Check if menu would close immediately
if game.test_enemy_menu_visible:
    menu_x = SCREEN_WIDTH - 290
    menu_y = 540
    menu_w = 270
    item_h = 35
    visible_count = 8
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, visible_count * item_h + 10)
    
    print(f"\nMenu rect: {menu_rect}")
    print(f"Click position: {test_pos}")
    print(f"Menu rect collidepoint: {menu_rect.collidepoint(test_pos)}")
    print(f"test_enemy_btn.is_clicked at click pos: {test_enemy_btn.is_clicked(test_pos)}")
    
    # Would menu close?
    if not menu_rect.collidepoint(test_pos) and not test_enemy_btn.is_clicked(test_pos):
        print("MENU WOULD CLOSE!")
    else:
        print("Menu stays open")