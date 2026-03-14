# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find MAP state in _handle_click
handle_start = content.find(b'def _handle_click(self, pos):')
map_start = content.find(b'elif self.game_state == "MAP":', handle_start)
pre_battle = content.find(b'elif self.game_state == "PRE_BATTLE":', map_start)

if map_start >= 0 and pre_battle >= 0:
    map_code = content[map_start:pre_battle]
    
    # Print all lines that have "next_enemy" in MAP click handling
    lines = map_code.decode('utf-8', errors='ignore').split('\n')
    for i, line in enumerate(lines):
        if 'next_enemy' in line.lower():
            print(f"Line {i}: {line}")
