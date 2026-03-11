#!/usr/bin/env python3
"""Dicey Dungeons — Точка входа"""
import sys
import pygame
pygame.init()
from modules.game import Game


def main():
    pygame.init()
    game = Game()

    # Валидация данных при старте
    from modules.core.validator import validate_game_data
    errors = validate_game_data()
    if errors:
        print("⚠️ Предупреждения валидации:")
        for e in errors:
            print(f"  - {e}")
        # Не прерываем, но логируем

    try:
        game.run()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()

#npx @kodadev/koda-cli