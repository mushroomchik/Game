# -*- coding: utf-8 -*-
import pygame
import sys
sys.path.insert(0, '.')

pygame.init()

from modules.game import Game

game = Game()
game._reset_game()

# Simulate clicking test_enemy_btn to open menu
btn = game.test_enemy_btn
pos = (btn.rect.x + btn.rect.width // 2, btn.rect.y + btn.rect.height // 2)
game.test_enemy_menu_visible = True

print("Menu is open")
print(f"test_enemies: {len(game.test_enemies)}")

# Try clicking on first enemy in the menu
# Menu position: SCREEN_WIDTH - 290, 540
# item_h = 35
# So first enemy button is at (SCREEN_WIDTH - 290, 540)

menu_x = 1200 - 290  # 910
menu_y = 540
item_h = 35

# Click on first enemy
enemy_pos = (menu_x + 100, menu_y + item_h // 2)  # center of first item
print(f"\nClicking on first enemy at {enemy_pos}")

# Simulate the menu item click logic
for i in range(len(game.test_enemies)):
    btn_rect_x = menu_x
    btn_rect_y = menu_y + i * item_h
    btn_rect_w = 270
    btn_rect_h = item_h
    
    rect = pygame.Rect(btn_rect_x, btn_rect_y, btn_rect_w, btn_rect_h)
    if rect.collidepoint(enemy_pos):
        enemy = game.test_enemies[i]
        print(f"Clicked on enemy {i}: {enemy['name']}")
        
        # Create enemy for battle
        from modules.entities import Enemy
        game.next_enemy = Enemy(
            name=enemy["name"],
            hp=enemy["hp"],
            damage_range=enemy["dmg"],
            image_path=f"assets/images/{enemy['icon']}.png",
            icon_type=enemy["icon"],
            enemy_type=enemy["enemy_type"],
            damage_type=enemy["dmg_type"]
        )
        game.test_enemy_menu_visible = False
        print(f"next_enemy set to: {game.next_enemy.name}")
        break