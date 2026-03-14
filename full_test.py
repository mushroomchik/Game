# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game

game = Game()
game._reset_game()

print("=== Testing full click flow ===")

# Get button position
btn = game.test_enemy_btn
click_pos = (btn.rect.centerx, btn.rect.centery)
print(f"1. Clicking at {click_pos}")
print(f"   Button rect: {btn.rect}")

# Check each condition in order
print(f"\n2. Checking conditions:")

# First check - game_state == "MAP"
print(f"   game_state == 'MAP': {game.game_state == 'MAP'}")

# Second check - test_enemy_btn.is_clicked
is_clicked = btn.is_clicked(click_pos)
print(f"   test_enemy_btn.is_clicked: {is_clicked}")

# Toggle menu
if is_clicked:
    game.test_enemy_menu_visible = not game.test_enemy_menu_visible
    game.test_enemy_scroll = 0
    print(f"   After toggle: test_enemy_menu_visible = {game.test_enemy_menu_visible}")

# Check cheat_btn (should NOT be clicked)
from modules.config import SCREEN_WIDTH
cheat_btn = game.cheat_btn
print(f"\n3. Checking cheat_btn at same position:")
print(f"   cheat_btn.is_clicked: {cheat_btn.is_clicked(click_pos)}")

# Check if menu would close
if game.test_enemy_menu_visible:
    menu_x = SCREEN_WIDTH - 290
    menu_y = 540
    menu_w = 270
    item_h = 35
    visible_count = 8
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, visible_count * item_h + 10)
    
    print(f"\n4. Menu close check:")
    print(f"   menu_rect: {menu_rect}")
    print(f"   menu_rect.collidepoint(click_pos): {menu_rect.collidepoint(click_pos)}")
    print(f"   test_enemy_btn.is_clicked(click_pos): {btn.is_clicked(click_pos)}")
    
    close_condition = not menu_rect.collidepoint(click_pos) and not btn.is_clicked(click_pos)
    print(f"   Would close: {close_condition}")
    
    if close_condition:
        print("   WARNING: Menu would close immediately!")
    else:
        print("   OK: Menu should stay open")