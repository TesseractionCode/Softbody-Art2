from dynamic_window import DynamicWindow
from particle import Particle
from static_body import StaticBody
from bounds import PolygonalBound
from pygame import Vector2, mouse, Surface
import pygame
from random import randint
from spring_bond import SpringBond
from time import sleep
from dynamic_object import Renderable, Updatable
from drawing import DrawState, BrushColors, floodFill
from simulation_builder import buildStaticbodies, buildSoftbodies

class SimulationState(Updatable, Renderable):

    def __init__(self):
        self.setDefaults()

    @staticmethod
    def fromCanvas(canvas: Surface, softbody_color: tuple, staticbody_color: tuple, 
                   edge_length: int, 
                   build_voxel_size: int,
                   particle_mass: int, spring_k: int):
        state = SimulationState()

        (state.particles, state.spring_bonds) = buildSoftbodies(canvas, softbody_color, build_voxel_size,
                                                                particle_mass, spring_k)
        state.staticbodies = buildStaticbodies(canvas, staticbody_color, edge_length)
        
        return state

    def setDefaults(self):
        self.spring_bonds = []
        self.particles = []
        self.staticbodies = []

    def update(self, dt):
        [spring_bond.update(dt) for spring_bond in self.spring_bonds]
        [particle.update(dt) for particle in self.particles]
        [staticbody.update(dt) for staticbody in self.staticbodies]

    def render(self, screen):
        [spring_bond.render(screen) for spring_bond in self.spring_bonds]
        [particle.render(screen) for particle in self.particles]
        [staticbody.render(screen) for staticbody in self.staticbodies]
        

class Simulation(DynamicWindow):
    
    MODE_DRAW = 0
    MODE_SIMULATE = 1

    BRUSH_SIZING_SPEED = 4
    BRUSH_MAX_RADIUS = 300
    BRUSH_MIN_RADIUS = 4

    BUILD_VOXEL_SIZE = 12 # Higher number = faster
    EDGE_LENGTH = 50 # Higher number = faster
    PARTICLE_MASS = 1
    SPRING_K = 1000

    def __init__(self, resolution, bg_color):
        super().__init__(resolution, bg_color)
        self.setup()

    def setup(self):
        self.draw_state = DrawState()
        self.mode = Simulation.MODE_DRAW
        self.simulation_state = SimulationState()
        # Transparent canvas to draw shapes on.
        #self.draw_canvas = pygame.Surface(self.resolution, pygame.SRCALPHA, 32)
        self.draw_canvas = pygame.Surface(self.resolution)
        self.draw_canvas.fill(BrushColors.erase)
        # Keep track of the last position on the canvas drawn to (to remove draw gaps between frames)
        self.last_draw_pos = None
        # Is this frame the start of a simulation mode
        self.simulation_start = False

        self.test_statics = []
        self.test_particles = []

    def updateDrawMode(self, dt, events):
        for event in events:

            if event.type == pygame.KEYDOWN:

                '''Switch brushes'''
                if event.key == pygame.K_1:
                    self.draw_state.brush = DrawState.BRUSH_SOFTBODY
                if event.key == pygame.K_2:
                    self.draw_state.brush = DrawState.BRUSH_STATICBODY
                if event.key == pygame.K_e:
                    self.draw_state.brush = DrawState.BRUSH_ERASE

                '''Clear canvas'''
                if event.key == pygame.K_BACKSPACE:
                    self.draw_canvas.fill(BrushColors.erase)

                '''Flood fill'''
                if event.key == pygame.K_f:
                    match self.draw_state.brush:
                        case DrawState.BRUSH_SOFTBODY:
                            floodFill(self.draw_canvas, BrushColors.softbody, mouse.get_pos())
                        case DrawState.BRUSH_STATICBODY:
                            floodFill(self.draw_canvas, BrushColors.staticbody, mouse.get_pos())

            # Reset the last drawn position to none when user stops drawing
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.last_draw_pos = None

            # Allow individual brush resizing
            if event.type == pygame.MOUSEWHEEL:
                r_delta = event.y * Simulation.BRUSH_SIZING_SPEED
                match self.draw_state.brush:
                    case DrawState.BRUSH_SOFTBODY:
                        self.draw_state.softbody_radius = max(Simulation.BRUSH_MIN_RADIUS, 
                                                              min(Simulation.BRUSH_MAX_RADIUS, 
                                                                  self.draw_state.softbody_radius + r_delta))
                    case DrawState.BRUSH_STATICBODY:
                         self.draw_state.staticbody_radius = max(Simulation.BRUSH_MIN_RADIUS, 
                                                              min(Simulation.BRUSH_MAX_RADIUS, 
                                                                  self.draw_state.staticbody_radius + r_delta))
                    case DrawState.BRUSH_ERASE:
                         self.draw_state.eraser_radius = max(Simulation.BRUSH_MIN_RADIUS, 
                                                              min(Simulation.BRUSH_MAX_RADIUS, 
                                                                  self.draw_state.eraser_radius + r_delta))

    def updateSimulateMode(self, dt, events):
        [p.applyForce(p.mass * Vector2(0,70)) for p in self.simulation_state.particles]
        self.simulation_state.update(dt)

    def renderDrawMode(self, screen):
        mouse_buttons = mouse.get_pressed()
        
        # Decide color and radius to draw with based off of brush in use
        match self.draw_state.brush:
            case DrawState.BRUSH_SOFTBODY:
                draw_color = BrushColors.softbody
                draw_radius = self.draw_state.softbody_radius
            case DrawState.BRUSH_STATICBODY:
                draw_color = BrushColors.staticbody
                draw_radius = self.draw_state.staticbody_radius
            case DrawState.BRUSH_ERASE:
                draw_color = BrushColors.erase
                draw_radius = self.draw_state.eraser_radius

        mouse_pos = mouse.get_pos()

        # Draw on left mouse button press
        if mouse_buttons[0]:
            pygame.draw.circle(self.draw_canvas, draw_color, mouse_pos, draw_radius)
            # Fill gap between this frame and the last frame
            if self.last_draw_pos:
                pygame.draw.line(self.draw_canvas, draw_color, self.last_draw_pos, mouse_pos, 2*draw_radius)
            self.last_draw_pos = mouse_pos

        # Render the draw canvas and the draw state/draw cursor
        screen.blit(self.draw_canvas, (0,0))
        self.draw_state.render(screen)

    def renderSimulateMode(self, screen):
        self.simulation_state.render(screen)

    def render(self, screen, res):
        match self.mode:
            case Simulation.MODE_DRAW:
                self.renderDrawMode(screen)
            case Simulation.MODE_SIMULATE:
                self.renderSimulateMode(screen)

    def update(self, dt, events):
        # Reset dt when simulation mode starts
        if self.simulation_start:
            self.simulation_start = False
            dt = 0

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    match self.mode:
                        case Simulation.MODE_DRAW:
                            # Generate softbodies and staticbodies and switch to simulation mode
                            self.simulation_state = SimulationState.fromCanvas(self.draw_canvas, 
                                                                            BrushColors.softbody, 
                                                                            BrushColors.staticbody, 
                                                                            Simulation.EDGE_LENGTH,
                                                                            Simulation.BUILD_VOXEL_SIZE,
                                                                            Simulation.PARTICLE_MASS,
                                                                            Simulation.SPRING_K)
                            
                            # Switch to simulate mode
                            self.mode = Simulation.MODE_SIMULATE
                            self.simulation_start = True
                        case Simulation.MODE_SIMULATE:
                            self.mode = Simulation.MODE_DRAW
                if event.key == pygame.K_SPACE:
                    for angle in range(0, 360, 20):
                        pos = Vector2(mouse.get_pos()[0], mouse.get_pos()[1])
                        vel = Vector2.from_polar((20, angle))
                        self.test_particles.append(Particle(pos, vel, 10))

        match self.mode:
            case Simulation.MODE_DRAW:
                self.updateDrawMode(dt, events)
            case Simulation.MODE_SIMULATE:
                self.updateSimulateMode(dt, events)


sim = Simulation((800, 600), (10, 10, 15))
sim.start()