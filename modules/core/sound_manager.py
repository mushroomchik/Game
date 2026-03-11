"""Звуковая система"""
import pygame
from modules.config import SOUND_ENABLED, SOUNDS


class SoundManager:
    _sounds = {}
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return
        if SOUND_ENABLED:
            pygame.mixer.init()
            for name, path in SOUNDS.items():
                try:
                    cls._sounds[name] = pygame.mixer.Sound(path)
                except:
                    pass  # Тихо игнорировать
        cls._initialized = True

    @classmethod
    def play(cls, name: str, volume: float = 1.0):
        if name in cls._sounds:
            sound = cls._sounds[name]
            sound.set_volume(volume)
            sound.play()

    @classmethod
    def stop(cls, name: str = None):
        if name and name in cls._sounds:
            cls._sounds[name].stop()
        elif name is None:
            pygame.mixer.stop()