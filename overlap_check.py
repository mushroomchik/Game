# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game
from modules.config import SCREEN_WIDTH

game = Game()
game._reset_game()

btn = game.test_enemy_btn

print("=== Checking overlap ===")
print(f"Button rect: {btn.rect}")
print(f"Button center: ({btn.rect.centerx}, {btn.rect.centery})")

# Menu position
menu_x = SCREEN_WIDTH - 290  # 910
menu_y = 540
menu_w = 270
item_h = 35
visible_count = 8

print(f"\nMenu rect: x={menu_x}, y={menu_y}, w={menu_w}, h={visible_count * item_h}")

# Check each menu item
print("\nMenu items:")
for i in range(visible_count):
    item_y = menu_y + i * item_h
    item_rect = pygame.Rect(menu_x, item_y, menu_w, item_h)
    print(f"  Item {i}: y={item_y}-{item_y+item_h}, rect={item_rect}")
    
    # Check if button center is inside this item
    if item_rect.collidepoint(btn.rect.centerx, btn.rect.centery):
        print(f"    ^^^ BUTTON CENTER IS INSIDE THIS ITEM!")

print(f"\nButton center: ({btn.rect.centerx}, {btn.rect.centery})")
print(f"Is inside menu area: {pygame.Rect(menu_x, menu_y, menu_w, visible_count * item_h).collidepoint(btn.rect.centerx, btn.rect.centery)}")