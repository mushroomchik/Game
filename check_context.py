# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

lines = content.decode('utf-8', errors='ignore').split('\n')

# Show context for each next_enemy = _create_enemy
for i, line in enumerate(lines):
    if 'next_enemy = self._create_enemy' in line:
        print(f"=== Line {i} ===")
        # Show 5 lines before
        for j in range(max(0, i-5), i):
            print(f"{j}: {lines[j]}")
        print(f"{i}: {line}")
        # Show 3 lines after
        for j in range(i+1, min(len(lines), i+4)):
            print(f"{j}: {lines[j]}")
        print()
