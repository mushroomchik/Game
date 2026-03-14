# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find _update method
update_start = content.find(b'def _update(self):')
if update_start >= 0:
    # Find next method after _update
    next_def = content.find(b'\n    def ', update_start + 10)
    if next_def >= 0:
        update_code = content[update_start:next_def]
        
        # Look for next_enemy in _update
        if b'next_enemy' in update_code:
            print("next_enemy is modified in _update()!")
            idx = update_code.find(b'next_enemy')
            print(update_code[idx:idx+200].decode('utf-8', errors='ignore'))
        else:
            print("No next_enemy modification in _update()")
            
# Also check if _create_enemy is called in MAP state
map_section = content.find(b'elif self.game_state == "MAP":')
pre_battle = content.find(b'elif self.game_state == "PRE_BATTLE":')

if map_section >= 0 and pre_battle >= 0:
    map_code = content[map_section:pre_battle]
    
    # Check if _create_enemy is called
    if b'_create_enemy' in map_code:
        print("\n_create_enemy is called in MAP state!")
        idx = map_code.find(b'_create_enemy')
        print(map_code[idx:idx+200].decode('utf-8', errors='ignore'))