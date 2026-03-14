# -*- coding: utf-8 -*-
import sys
import os
import codecs

os.chdir(r'C:\Users\USER\PycharmProjects\Game')
sys.path.insert(0, '.')

output = []

# Test imports
try:
    from modules.config import display
    output.append("display.py OK")
except Exception as e:
    output.append(f"display.py ERROR: {e}")

try:
    from modules.config import gameplay
    output.append("gameplay.py OK")
except Exception as e:
    output.append(f"gameplay.py ERROR: {e}")

try:
    from modules.entities import Enemy, Dice, CharacterIcon, Armor
    output.append("entities OK")
except Exception as e:
    output.append(f"entities ERROR: {e}")

try:
    from modules.cards import AbilityCard
    output.append("AbilityCard OK")
except Exception as e:
    output.append(f"AbilityCard ERROR: {e}")

try:
    from modules.systems import BattleManager, MapManager, InventoryManager
    output.append("systems OK")
except Exception as e:
    output.append(f"systems ERROR: {e}")

try:
    from modules.ui import GameRenderer
    output.append("GameRenderer OK")
except Exception as e:
    output.append(f"GameRenderer ERROR: {e}")

# Test creating game
output.append("\n--- Testing Game class ---")
try:
    import ast
    with open('modules/game.py', 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    output.append("game.py syntax OK")
except Exception as e:
    output.append(f"game.py syntax ERROR: {e}")

output.append("\nDone!")

# Write to file
with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))