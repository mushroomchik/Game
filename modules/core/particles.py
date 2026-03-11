"""Система частиц для визуальных эффектов"""
import random
import pygame


class Particle:
    def __init__(self, x: float, y: float, color: tuple,
                 lifetime: int = 30, velocity: tuple = None, size: int = None):
        self.x, self.y = x, y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx, self.vy = velocity or (random.uniform(-1, 1), random.uniform(-2, -0.5))
        self.size = size or random.randint(2, 5)
        self.alpha = 255

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0 and self.size > 0.5

    def draw(self, screen: pygame.Surface):
        if self.alpha <= 0:
            return
        surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, self.alpha),
                           (int(self.size), int(self.size)), int(self.size))
        screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x: float, y: float, color: tuple, count: int = 10, **kwargs):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, **kwargs))

    def emit_damage(self, x: float, y: float, damage_type: str = "normal"):
        from modules.config import ELEMENT_COLORS
        color = ELEMENT_COLORS.get(damage_type, (255, 100, 100))
        self.emit(x, y, color, count=15, velocity=(random.uniform(-2, 2), random.uniform(-3, -1)))

    def emit_heal(self, x: float, y: float):
        self.emit(x, y, (100, 255, 100), count=20, velocity=(0, -1.5), size=3)

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen: pygame.Surface):
        for particle in self.particles:
            particle.draw(screen)