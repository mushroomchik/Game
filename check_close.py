# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find the section that closes test_enemy_menu
handle_start = content.find(b'def _handle_click(self, pos):')
map_start = content.find(b'elif self.game_state == "MAP":', handle_start)
pre_battle = content.find(b'elif self.game_state == "PRE_BATTLE":', map_start)

map_code = content[map_start:pre_battle]

# Find where test_enemy_menu_visible = False is set
idx = 0
while True:
    idx = map_code.find(b'test_enemy_menu_visible = False', idx)
    if idx < 0:
        break
    print("Found test_enemy_menu_visible = False at offset", idx)
    print("Context:")
    print(map_code[idx-100:idx+150].decode('utf-8', errors='ignore'))
    print("---")
    idx += 1
