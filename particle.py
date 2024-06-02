from dynamic_object import Renderable, Updatable
from pygame import Vector2, draw
from math import sqrt

class Particle(Renderable, Updatable):

    RENDER = True
    RENDER_RADIUS = 2
    RENDER_COLOR = (150, 160, 20)

    particles = []

    def __init__(self, pos: Vector2, vel: Vector2, mass: float):
        self.pos = pos
        self.vel = vel
        self.accel = Vector2(0,0)
        self.mass = mass

        self._net_force = Vector2(0,0)

        Particle.particles.append(self)

    def applyForce(self, force: Vector2):
        self._net_force += force
    
    def render(self, screen):
        if not Particle.RENDER: return
        draw.circle(screen, Particle.RENDER_COLOR, (self.pos.x, self.pos.y), Particle.RENDER_RADIUS)

    def update(self, dt):
        self.accel = self._net_force / self.mass
        # Eulers integration
        self.vel += self.accel * dt
        self.pos += self.vel * dt

        for particle in Particle.particles:
            if particle == self:
                continue
            squared_dist = (particle.pos - self.pos).magnitude_squared()
            if squared_dist == 0:
                continue
            if squared_dist <= 5**2:
                push_normal = (particle.pos - self.pos).normalize();
                dist = sqrt(squared_dist)
                delta = 5 - dist
                particle.pos += delta * push_normal
                particle.vel = particle.vel.reflect(push_normal)

        # Reset net force for next iteration
        self._net_force = Vector2(0,0)