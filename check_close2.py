# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Find the exact condition that closes the menu
handle_start = content.find(b'def _handle_click(self, pos):')
map_start = content.find(b'elif self.game_state == "MAP":', handle_start)

map_code = content[map_start:map_start+10000]

# Find the close menu code
idx = map_code.find(b'not self.test_enemy_btn.is_clicked(pos)')
if idx >= 0:
    print("Closing condition:")
    print(map_code[idx-50:idx+100].decode('utf-8', errors='ignore'))
