from pygame import Vector2, surfarray, Surface, draw
from static_body import StaticBody
from particle import Particle
from spring_bond import SpringBond
from bounds import PolygonalBound

def buildStaticbodies(canvas: Surface, body_color, voxel_size) -> list[StaticBody]:
    body_color = canvas.map_rgb((body_color[0], body_color[1], body_color[2], 255))
    canvas_array = surfarray.pixels2d(canvas)
    # Canvas dimensions
    canvas_width = len(canvas_array[0])
    canvas_height = len(canvas_array)
    '''Find staticbody pixels adjacent to either the edge of the canvas or
    to a non-staticbody pixel.'''
    edge_points = []
    for y in range(canvas_height):
        for x in range(canvas_width):
            # Ignore this pixel if not staticbody
            if canvas_array[y][x] != body_color:
                continue
            # Plot adjacent pixels including this one (True for staticbody, False for not)
            flattened_adjacent_map = []
            for ix in range(-1, 2):
                for iy in range(-1, 2):
                    if ((x+ix < 0) or (x+ix >= canvas_width) or
                        (y+iy < 0) or (y+iy >= canvas_height)):
                        flattened_adjacent_map.append(False)
                    else:
                        flattened_adjacent_map.append(canvas_array[y+iy][x+ix] == body_color)
            # Add this pixel if one or more of the adjacent pixels are not a staticbody
            if (not flattened_adjacent_map[4]) in flattened_adjacent_map:
                edge_points.append((y, x))
    
    '''Get shapes from edge points'''
    points_queue = edge_points
    shapes = []
    while len(points_queue) > 0:
        shape = [points_queue[0]]
        points_queue.remove(points_queue[0])

        is_chain_complete = len(points_queue) == 0
        while not is_chain_complete:
            current_point = shape[-1]

            # Points and their squared distances [((x, y), squared_distance)]
            point_distances = []
            for point in points_queue:
                squared_dist = (current_point[0] - point[0])**2 + (current_point[1] - point[1])**2
                point_distances.append((point, squared_dist))

            # Find the point with the smallest distance
            closest_point_data = min(point_distances, key=lambda data: data[1])
            closest_point = closest_point_data[0]
            closest_point_s_dist = closest_point_data[1]

            # Complete the chain if the closest point is not an adjacent voxel
            is_chain_complete = closest_point_s_dist > 2
            
            # Otherwise add the closest point to the shape
            if not is_chain_complete:
                shape.append(closest_point)
                points_queue.remove(closest_point)
                if len(points_queue) == 0:
                    is_chain_complete = True
        
        shapes.append(shape)

    # Reduce the number of point in each shape
    shapes = [[shape[i] for i in range(0, len(shape), voxel_size)] for shape in shapes]

    # Make sure there are no shapes with <3 verts
    shapes = [shape for shape in shapes if len(shape) >= 3]

    return [StaticBody(PolygonalBound(shape)) for shape in shapes]


def buildSoftbodies(canvas: Surface, body_color, voxel_size, particle_mass, spring_k) -> tuple[list[Particle], list[SpringBond]]:
    body_color = canvas.map_rgb((body_color[0], body_color[1], body_color[2], 255))
    canvas_array = surfarray.pixels2d(canvas)
    # Canvas dimensions
    canvas_width = len(canvas_array)
    canvas_height = len(canvas_array[0])

    '''Create a map of particles vs empty space (None). Wider than the canvas'''
    voxel_resolution = (int(canvas_width / voxel_size), int(canvas_height / voxel_size))
    particle_map = []
    created_particles = [] # Keep track of created particles
    for vx in range(-1, voxel_resolution[0] + 1):
        column = []
        for vy in range(-1, voxel_resolution[1] + 1):
            # Center coords of the voxel
            x_center = vx * voxel_size + int(voxel_size/2)
            y_center = vy * voxel_size + int(voxel_size/2)
            if ((x_center < 0) or (x_center >= canvas_width) or
                (y_center < 0) or (y_center >= canvas_height)):
                # Center pixel is not on the canvas
                column.append(None)
            else:
                if canvas_array[x_center][y_center] == body_color:
                    particle = Particle(Vector2(x_center, y_center),
                                                      Vector2(0,0), 
                                                      particle_mass)
                    column.append(particle)
                    created_particles.append(particle)
                else:
                    column.append(None)
        particle_map.append(column)
    
    '''Create bonds between particles in adjacent voxels.'''
    created_bonds = []
    for vx in range(voxel_resolution[0]):
        for vy in range(voxel_resolution[1]):
            if not particle_map[vx][vy]:
                continue
            current_particle = particle_map[vx][vy]

            if particle_map[vx + 1][vy]:
                created_bonds.append(SpringBond(current_particle, particle_map[vx + 1][vy], spring_k))
            if particle_map[vx][vy + 1]:
                created_bonds.append(SpringBond(current_particle, particle_map[vx][vy + 1], spring_k))
            if particle_map[vx + 1][vy + 1]:
                created_bonds.append(SpringBond(current_particle, particle_map[vx + 1][vy + 1], spring_k))
            if particle_map[vx + 1][vy - 1]:
                created_bonds.append(SpringBond(current_particle, particle_map[vx + 1][vy - 1], spring_k))

    return(created_particles, created_bonds)