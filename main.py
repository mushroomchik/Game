#!/usr/bin/env python3
"""
Dicey Dungeons - Python Edition
Точка входа в игру
"""

import sys
import os

# Добавляем корневую папку в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()