from dynamic_object import Renderable
from pygame import mouse, draw, SRCALPHA, Surface, surfarray

# Taken from https://stackoverflow.com/questions/41656764/how-to-implement-flood-fill-in-a-pygame-surface
def floodFill(canvas: Surface, color, start_position):
    color = canvas.map_rgb(color)  # Convert the color to mapped integer value.
    surf_array = surfarray.pixels2d(canvas)  # Create an array from the surface.
    current_color = surf_array[start_position]  # Get the mapped integer color value.

    frontier = [start_position]
    while len(frontier) > 0:
        x, y = frontier.pop()
        try:  # Add a try-except block in case the position is outside the surface.
            if surf_array[x, y] != current_color:
                continue
        except IndexError:
            continue
        surf_array[x, y] = color
        # Then we append the neighbours of the pixel in the current position to our 'frontier' list.
        frontier.append((x + 1, y))
        frontier.append((x - 1, y))
        frontier.append((x, y + 1))
        frontier.append((x, y - 1))

    surfarray.blit_array(canvas, surf_array)


class BrushColors:
    softbody = (50, 140, 40)
    staticbody = (100, 100, 100)
    erase = (10, 10, 15)

class DrawState(Renderable):

    BRUSH_SOFTBODY = 0
    BRUSH_STATICBODY = 1
    BRUSH_ERASE = 2

    SOFTBODY_CURSOR_COLOR = (255, 0, 0)
    STATICBODY_CURSOR_COLOR = (0, 255, 0)
    ERASER_CURSOR_COLOR = (255, 255, 255)
    CURSOR_CIRCLE_THICKNESS = 2

    def __init__(self): self.setDefaultValues()

    def setDefaultValues(self):
        self.brush = DrawState.BRUSH_SOFTBODY
        self.softbody_radius = 50
        self.staticbody_radius = 50
        self.eraser_radius = 70

    def render(self, screen):
        match self.brush:
            case DrawState.BRUSH_SOFTBODY:
                draw.circle(screen, DrawState.SOFTBODY_CURSOR_COLOR,
                                   mouse.get_pos(), self.softbody_radius, DrawState.CURSOR_CIRCLE_THICKNESS)
            case DrawState.BRUSH_STATICBODY:
                draw.circle(screen, DrawState.STATICBODY_CURSOR_COLOR,
                                   mouse.get_pos(), self.staticbody_radius, DrawState.CURSOR_CIRCLE_THICKNESS)
            case DrawState.BRUSH_ERASE:
                draw.circle(screen, DrawState.ERASER_CURSOR_COLOR,
                                   mouse.get_pos(), self.eraser_radius, DrawState.CURSOR_CIRCLE_THICKNESS)
                