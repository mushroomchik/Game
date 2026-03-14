# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find _reset_game and see where test_enemy_btn is created
reset_start = content.find(b'def _reset_game(self):')
if reset_start >= 0:
    reset_end = content.find(b'def run(self):', reset_start)
    if reset_end >= 0:
        reset_code = content[reset_start:reset_end]
        
        # Find test_enemy_btn
        idx = reset_code.find(b'test_enemy_btn')
        if idx >= 0:
            print("test_enemy_btn in _reset_game:")
            print(reset_code[idx:idx+200].decode('utf-8', errors='ignore'))
        else:
            print("test_enemy_btn NOT found in _reset_game!")
            
        # Find test_enemies initialization
        idx2 = reset_code.find(b'test_enemies')
        if idx2 >= 0:
            print("\ntest_enemies in _reset_game:")
            print(reset_code[idx2:idx2+150].decode('utf-8', errors='ignore'))