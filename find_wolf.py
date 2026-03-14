# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Search for code that sets next_enemy to wolf or changes it
patterns = [
    b'next_enemy =',
    b'wolf',
    b'slime'
]

for p in patterns:
    count = content.count(p)
    print(f"{p.decode()}: {count} times")
    
# Find where next_enemy is set in MAP state
map_section = content.find(b'elif self.game_state == "MAP":')
pre_battle = content.find(b'elif self.game_state == "PRE_BATTLE":')

if map_section >= 0 and pre_battle >= 0:
    map_code = content[map_section:pre_battle]
    
    # Find all next_enemy assignments in MAP
    idx = 0
    while True:
        idx = map_code.find(b'next_enemy', idx)
        if idx < 0:
            break
        print("\nnext_enemy in MAP section:")
        print(map_code[idx:idx+150].decode('utf-8', errors='ignore'))
        idx += 1
