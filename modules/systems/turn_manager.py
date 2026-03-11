"""Управление ходами"""
import pygame

class TurnManager:
    def __init__(self):
        self.turn = "PLAYER"  # "PLAYER" или "ENEMY"
        self._enemy_pending = False
        self._timer_set = False

    def start_enemy_turn(self, callback, delay_ms: int = 1500):
        """Запланировать ход врага"""
        if self._enemy_pending or self.turn != "PLAYER":
            return False
        self._enemy_pending = True
        self.turn = "ENEMY"
        # Сброс и установка таймера
        pygame.time.set_timer(pygame.USEREVENT, 0)
        pygame.time.set_timer(pygame.USEREVENT, delay_ms)
        self._timer_set = True
        return True

    def on_enemy_turn_event(self, callback):
        """Обработка события USEREVENT для хода врага"""
        if self.turn == "ENEMY" and self._enemy_pending:
            self._enemy_pending = False
            pygame.time.set_timer(pygame.USEREVENT, 0)
            self._timer_set = False
            callback()
            return True
        return False

    def end_enemy_turn(self):
        """Завершение хода врага"""
        self.turn = "PLAYER"
        self._enemy_pending = False

    def is_player_turn(self) -> bool:
        return self.turn == "PLAYER"