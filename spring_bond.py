from dynamic_object import Updatable, Renderable
from particle import Particle
from pygame import Vector2, draw

class SpringBond(Updatable, Renderable):

    RENDER = True
    RENDER_COLOR = (200, 200, 220)
    RENDER_THICKNESS = 2

    def __init__(self, particle1: Particle, particle2: Particle, k: float):
        self.p1 = particle1
        self.p2 = particle2
        self.k = k
        self.initial_length = self._getLength()

    def _getLength(self):
        return (self.p2.pos - self.p1.pos).magnitude()
    
    def _getSpringVector(self):
        '''Get the normalized vector pointing from particle 1 to 2.'''
        return (self.p2.pos - self.p1.pos).normalize()

    def update(self, dt):
        length = self._getLength()
        # Ignore this frame if the distance between the particles is zero
        if length == 0: return
        
        length_delta = length - self.initial_length
        resistance = self.k * length_delta

        damping = (self.p2.pos - self.p1.pos).normalize() * (self.p2.vel - self.p1.vel) * 10

        spring_vec = self._getSpringVector()
        self.p1.applyForce((resistance + damping) * spring_vec)
        self.p2.applyForce((resistance + damping) * -spring_vec)

    def render(self, screen):
        if not SpringBond.RENDER: return
        draw.line(screen, SpringBond.RENDER_COLOR, 
                  (self.p1.pos.x, self.p1.pos.y),
                  (self.p2.pos.x, self.p2.pos.y),
                  SpringBond.RENDER_THICKNESS)
    