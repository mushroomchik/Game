# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Check the exact structure of MAP handling in _handle_click
handle_start = content.find(b'def _handle_click(self, pos):')
map_start = content.find(b'elif self.game_state == "MAP":', handle_start)

# Find test_enemy_btn click handler
btn_handler = content.find(b'self.test_enemy_btn.is_clicked', map_start)

# Print from test_enemy_btn to the end of MAP section
pre_battle = content.find(b'elif self.game_state == "PRE_BATTLE":', map_start)

print("Code from test_enemy_btn click to end of MAP section:")
print(content[btn_handler:pre_battle].decode('utf-8', errors='ignore'))
