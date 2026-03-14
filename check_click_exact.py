# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find _handle_click and then find exact test_enemy_btn handling
handle_start = content.find(b'def _handle_click(self, pos):')
if handle_start >= 0:
    # Find test_enemy_btn click
    btn_click = content.find(b'test_enemy_btn.is_clicked', handle_start)
    if btn_click >= 0:
        # Show the exact code block
        print("test_enemy_btn click handling:")
        print(content[btn_click-50:btn_click+150].decode('utf-8', errors='ignore'))
        
        # Now find what comes AFTER this - the next elif/if
        next_line = content.find(b'\n            elif', btn_click)
        if next_line < 0:
            next_line = content.find(b'\n            if', btn_click)
        
        if next_line >= 0 and next_line < btn_click + 500:
            print("\n\nWhat comes AFTER test_enemy_btn click:")
            print(content[btn_click:next_line+200].decode('utf-8', errors='ignore'))