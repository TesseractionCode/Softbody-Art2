from pygame import Vector3

class Boundary:

    def contains(self, point: tuple) -> bool:
        pass


class RectangularBound(Boundary):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point: tuple) -> bool:
        return ((point[0] >= self.x) and (point[0] <= self.x + self.width) and
                (point[1] >= self.y) and (point[1] <= self.y + self.height))
    

class CircularBound(Boundary):

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def contains(self, point: tuple) -> bool:
        return (self.x - point[0])**2 + (self.y - point[1])**2 <= self.radius


class PolygonalBound(Boundary):

    def __init__(self, points: list[tuple]):
        self.points = points

        # Calculate rectangle boundary for collision optimization
        self.rectangle_bound = PolygonalBound.getRectangularBounds(self)

    @staticmethod
    def getRectangularBounds(polygonal_bounds) -> RectangularBound:
        points = polygonal_bounds.points
        min_x, min_y = points[0][0], points[0][1]
        max_x, max_y = points[0][0], points[0][1]
        for point in points:
            if point[0] < min_x:
                min_x = point[0]
            if point[1] < min_y:
                min_y = point[1]
            if point[0] > max_x:
                max_x = point[0]
            if point[1] > max_y:
                max_y = point[1]

        width = max_x - min_x
        height = max_y - min_y

        return RectangularBound(min_x, min_y, width, height)
    
    def getClosestEdgeToPoint(self, point: tuple) -> list[tuple]:
        '''Gets the pair of points representing the polygon's closest 
        edge the given point.'''
        edge_distances = []
        for i in range(len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            
            AC = Vector3(point[0] - p1[0], point[1] - p1[1], 0)
            AB = Vector3(p2[0] - p1[0], p2[1] - p1[1], 0)

            distance_squared = AC.cross(AB).magnitude_squared() / AB.magnitude_squared()
            edge_distances.append(((p1, p2), distance_squared))
        
        # Pick out the edge with the smallest distance to the point
        closest_edge_points = min(edge_distances, key=lambda edge: edge[1])[0]
        return closest_edge_points

    def contains(self, point: tuple) -> bool:
        if not self.rectangle_bound.contains(point):
            return False
        # "Raytrace" downwards from point
        num_intersections = 0
        for i in range(len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]

            # Sort the points horizontally
            sorted_points = [p1, p2]
            sorted_points.sort(key=lambda p: p[0])
            p1, p2 = sorted_points
            # Skip vertical lines
            if p2[0] - p1[0] == 0:
                continue
            # Skip a line if it is not underneath the point
            if not ((point[0] >= p1[0]) and (point[0] <= p2[0])):
                continue
            # Find the vertical point of intersection of the ray cast on this line
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            b = p1[1] - m*p1[0]
            point_y = m*point[0] + b
            # Don't count lines that intersect above the point
            if point_y >= point[1]:
                num_intersections += 1
        
        return num_intersections % 2 == 1


