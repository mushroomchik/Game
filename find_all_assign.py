# -*- coding: utf-8 -*-
content = open('modules/game.py', 'rb').read()

# Search for all places where next_enemy is assigned
lines = content.decode('utf-8', errors='ignore').split('\n')
for i, line in enumerate(lines):
    if 'next_enemy' in line and '=' in line and 'next_enemy =' in line:
        # Get function context
        func_start = i
        while func_start > 0 and 'def ' not in lines[func_start]:
            func_start -= 1
        func_name = lines[func_start] if 'def ' in lines[func_start] else 'unknown'
        
        print(f"Line {i}: {line.strip()}")
        print(f"  In: {func_name.strip()}")
        print()