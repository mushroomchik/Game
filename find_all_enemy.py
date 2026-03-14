# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Search ALL code for next_enemy = Enemy(
idx = 0
while True:
    idx = content.find(b'next_enemy = Enemy(', idx)
    if idx < 0:
        break
    print("Found at position", idx)
    # Find what function this is in
    # Go backwards to find def
    func_start = content.rfind(b'def ', 0, idx)
    if func_start >= 0:
        func_line = content.find(b'\n', func_start)
        func_name = content[func_start:func_line].decode('utf-8', errors='ignore')
        print(f"  In function: {func_name}")
    print("  Context:")
    print(content[idx:idx+200].decode('utf-8', errors='ignore'))
    print("---")
    idx += 1
