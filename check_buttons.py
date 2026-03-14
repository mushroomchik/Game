# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find all button positions in __init__
init_start = content.find(b'def __init__(self):')
init_end = content.find(b'def _reset_game(self):')

if init_start >= 0 and init_end >= 0:
    init_code = content[init_start:init_end]
    
    # Find test_enemy_btn
    idx = init_code.find(b'test_enemy_btn = Button')
    if idx >= 0:
        print("test_enemy_btn position:")
        print(init_code[idx:idx+100].decode('utf-8', errors='ignore'))
    
    # Find cheat_btn
    idx = init_code.find(b'cheat_btn = Button')
    if idx >= 0:
        print("\ncheat_btn position:")
        print(init_code[idx:idx+100].decode('utf-8', errors='ignore'))
    
    # Find inventory_btn
    idx = init_code.find(b'inventory_btn = Button')
    if idx >= 0:
        print("\ninventory_btn position:")
        print(init_code[idx:idx+150].decode('utf-8', errors='ignore'))
