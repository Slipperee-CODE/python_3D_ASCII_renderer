from operator import add
from operator import sub
from operator import mul
from math import sqrt

class Vector:
    def __init__(self, v:list[float]):
        self.v = v

        Vector.add = self.create_operation_func(add)
        Vector.subtract = self.create_operation_func(sub)
        
        Vector.vector_multiply = self.create_operation_func(mul)
        Vector.scalar_multiply = lambda f, c: Vector.vector_multiply(f, Vector([c for _ in range(len(f))]))

        Vector.dot_product = lambda f, g: sum(Vector.vector_multiply(f, g))
        Vector.length = lambda f: sqrt(Vector.dot_product(f,f))
        Vector.normalize = lambda f: Vector.scalar_multiply(f, 1 / Vector.length(f))

    def __iter__(self):
        return iter(self.v)

    def __len__(self):
        return len(self.v)

    def __repr__(self):
        return f"Vector({str(self.v)})"

    @staticmethod 
    def checkThatLengthsMatch(f, g): 
        if (len(f) != len(g)):
            raise ValueError(f"dot_product cannot be performed on vectors {f} and {g} of len {len(f)} and {len(g)}")
    
    @staticmethod
    def create_operation_func(operation):
        def operation_func(f, g):
            Vector.checkThatLengthsMatch(f, g)
            h = [operation(f.v[i],g.v[i]) for i in range(len(f))] 
            return Vector(h)
        return operation_func
    
class RenderablePlane():
    def __init__(self, c:Vector, n:Vector, width:float, length:float):
        self.c = c
        self.n = Vector.normalize(n)
        self.width = width
        self.length = length 

    def collides(self, p:Vector, tolerance=0):
        return Vector.dot_product(self.n, Vector.subtract(self.c, p)) <= tolerance

class Ray():
    def __init__(self, start_pos:Vector, direction:Vector, deltaAdvance:float = 0.1):
        self.curr_pos = start_pos
        self.direction = Vector.normalize(direction)
        self.deltaAdvance = deltaAdvance
        self.hasCollided = False

    def advance(self) -> None:
        # curr_pos += direction * deltaAdvance 
        # check for collision somehow and update hasCollided accordingly
        ...

    def collided(self) -> bool:
        return self.hasCollided
        
