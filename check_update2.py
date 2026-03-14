# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Check _update method for any next_enemy changes
update_start = content.find(b'def _update(self):')
if update_start >= 0:
    # Find next method to get full _update code
    next_def = content.find(b'\n    def ', update_start + 20)
    if next_def < 0:
        next_def = len(content)
    
    update_code = content[update_start:next_def]
    
    # Check if _create_enemy is called in _update
    if b'_create_enemy' in update_code:
        print("_create_enemy IS called in _update()!")
        idx = update_code.find(b'_create_enemy')
        print(update_code[idx:idx+200].decode('utf-8', errors='ignore'))
    else:
        print("_create_enemy is NOT called in _update()")
        
    # Check if next_enemy is set in _update
    if b'next_enemy =' in update_code:
        print("\nnext_enemy IS set in _update()!")
        idx = update_code.find(b'next_enemy =')
        print(update_code[idx:idx+200].decode('utf-8', errors='ignore'))
    else:
        print("\nnext_enemy is NOT set in _update()")
