from math import sqrt

class Point:

    radius = 20
    connected_poinrs = []

    def __init__(self, id, x, y):
        self.id = id
        self.x = x 
        self.y = y

class Line:

    def __init__(self, point1, point2, epsilon=1):
        self.point1 = point1
        self.point2 = point2
        self.x1, self.y1 = point1.x, point1.y
        self.x2, self.y2 = point2.x, point2.y 
        self.epsilon = epsilon
        self.len = round(sqrt( (point2.x-point1.x)**2 + (point2.y-point1.y)**2 ), 3)
    