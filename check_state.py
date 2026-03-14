# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find game_state initialization in __init__
init_start = content.find(b'def __init__(self):')
init_end = content.find(b'def _reset_game(self):')
init_code = content[init_start:init_end]

# Find game_state
idx = init_code.find(b'game_state')
if idx >= 0:
    print("game_state in __init__:")
    print(init_code[idx:idx+100].decode('utf-8', errors='ignore'))
