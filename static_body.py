from dynamic_object import Updatable, Renderable
from bounds import PolygonalBound
from pygame import Vector2, draw
from particle import Particle

class StaticBody(Updatable, Renderable):

    RENDER_VERTEX_COLOR = (200, 200, 10)
    RENDER_VERTEX_RADIUS = 3
    RENDER_EDGE_COLOR = (220, 220, 220)
    RENDER_EDGE_WIDTH = 2
    RENDER_FILL_COLOR = (20, 20, 30)
    RENDER_VERTS = False
    RENDER_EDGES = True
    RENDER_FILL = True

    def __init__(self, shape: PolygonalBound):
        self.shape = shape

        # Determine normal flipper (direction of normals)
        self._normal_flipper = -1
        p1, p2 = self.shape.points[0], self.shape.points[1]
        D = Vector2(p2[0] - p1[0], p2[1] - p1[1])
        mid = Vector2(p1[0], p1[1]) + D / 2
        projection_point = mid + D.normalize().rotate(90)
        if self.shape.contains((projection_point.x, projection_point.y)):
            self._normal_flipper = 1

    def containsParticle(self, particle: Particle) -> bool:
        return self.shape.contains((particle.pos.x, particle.pos.y))

    def update(self, dt):
        for particle in Particle.particles:
            # Ignore particle if it hasn't collided
            if not self.containsParticle(particle):
                continue
            # Determine which edge was hit
            hit_edge_points = self.shape.getClosestEdgeToPoint((particle.pos.x, particle.pos.y))
            # Reflect off of colliding edge
            l = Vector2(hit_edge_points[0][0] - hit_edge_points[1][0], hit_edge_points[0][1] - hit_edge_points[1][1])
            N = l.rotate(90).normalize() * self._normal_flipper
            # Push the particle out of the static body
            particle.pos += 2 * particle.vel.magnitude() * N * dt
            particle.vel = particle.vel.reflect(N)

    def render(self, screen):
        # Fill
        if StaticBody.RENDER_FILL:
            draw.polygon(screen, StaticBody.RENDER_FILL_COLOR, self.shape.points)
        # Draw edges
        if StaticBody.RENDER_EDGES:
            draw.lines(screen, StaticBody.RENDER_EDGE_COLOR, True, self.shape.points, StaticBody.RENDER_EDGE_WIDTH)
        # Draw verts
        if StaticBody.RENDER_VERTS:
            for point in self.shape.points:
                draw.circle(screen, StaticBody.RENDER_VERTEX_COLOR, point, StaticBody.RENDER_VERTEX_RADIUS)