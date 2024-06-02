from time import time
import pygame

pygame.init()

class DynamicWindow:
    '''A window that persistently updates and re-renders. Good for game graphics, physics
    and animations.'''

    def __init__(self, resolution, bg_color):
        self.resolution = resolution
        self.bg_color = bg_color

        self.is_running = False
        self.screen = None
        self.frame = 0

    def start(self):
        self.screen = pygame.display.set_mode(self.resolution)
        self.is_running = True

        dt = 0
        while self.is_running:
            start_time = time()
            
            events = pygame.event.get()
            for event in events:
                
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    break

            if not self.is_running:
                break

            self.update(dt, events)
            self.render(self.screen, self.resolution)
            pygame.display.flip()

            self.screen.fill(self.bg_color)
            self.frame += 1

            dt = time() - start_time

    def stop(self):
        self.is_running = False
    
    def update(self, dt, events):
        pass

    def render(self, screen, res):
        pass