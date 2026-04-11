from operator import add
from operator import sub
from operator import mul
from math import sqrt
from math import cos
from math import sin
from math import pi
from typing import Callable
from time import sleep

def setup_vector_operations(cls:type) -> type:
    def checkThatLengthsMatch(operation:Callable, f, g): 
        if (len(f) != len(g)):
            raise ValueError(f"{operation.__name__} cannot be performed on vectors {f} and {g} of len {len(f)} and {len(g)}")

    def create_operation_func(operation:Callable) -> Callable:
        def operation_func(f, g):
            checkThatLengthsMatch(operation, f, g)
            h:list[float] = [operation(f[i],g[i]) for i in range(len(f))] 
            return cls(h)
        return operation_func

    cls.add = create_operation_func(add)
    cls.subtract = create_operation_func(sub)
    cls.vector_multiply = create_operation_func(mul)

    cls.scalar_multiply = lambda c, f: cls.vector_multiply(f, cls([c for _ in range(len(f))]))
    cls.dot_product = lambda f, g: sum(cls.vector_multiply(f, g))
    cls.length = lambda f: sqrt(cls.dot_product(f,f))
    cls.normalize = lambda f: cls.scalar_multiply(1 / cls.length(f), f)

    cls.cross_product = lambda f, g: Vector((f[1]*g[2] - f[2]*g[1], f[2]*g[0] - f[0]*g[2], f[0]*g[1] - f[1]*g[0]))

    return cls

@setup_vector_operations
class Vector(tuple[float]):
    def __init__(self, v:tuple[float]):
        self = v

    def __repr__(self):
        return f"Vector({[self[i] for i in range(len(self))]})"
    
class RenderableManager():
    renderables:list["Renderable"] = []

    def __repr__(self):
        return str(self.renderables)

class Renderable():
    def __init__(self):
        RenderableManager.renderables.append(self)

    def collides(self, p:Vector, tolerance:float=0) -> bool: ...

class RenderableDisk(Renderable):
    def __init__(self, c:Vector, n:Vector, radius:float):
        super().__init__()
        self.c = c
        self.n = Vector.normalize(n)
        self.radius = radius

    def rotate(self, degrees, axisOfRotation:Vector):
        radians = degrees*pi/180
        axisOfRotation = Vector.normalize(axisOfRotation)

        # This just uses a formula that exists from rotating a vector around an arbitrary axis - Cai
        self.n = Vector.add(
            Vector.add(
                Vector.scalar_multiply(cos(radians), self.n), 
                Vector.scalar_multiply(sin(radians), Vector.cross_product(axisOfRotation, self.n))
            ),
            Vector.scalar_multiply((1-cos(radians))*Vector.dot_product(self.n, axisOfRotation),axisOfRotation)
        )
        
    def collides(self, p:Vector, tolerance:float=0) -> bool:
        isWithinPlaneOfDisk:bool = Vector.dot_product(self.n, Vector.subtract(self.c, p)) <= tolerance
        isWithinDiskRadius:bool = Vector.length(Vector.subtract(self.c, p)) <= self.radius
        return isWithinPlaneOfDisk and isWithinDiskRadius

class Ray:
    def __init__(self, startPos:Vector, direction:Vector, deltaAdvance:float=0.1):
        self.startPos = startPos
        self.currPos = startPos
        self.direction = Vector.normalize(direction)
        self.deltaAdvance = deltaAdvance

    def length(self) -> float:
        return Vector.length(Vector.subtract(self.startPos, self.currPos))

    def advance(self):
        self.currPos = Vector.add(self.currPos, Vector.scalar_multiply(self.deltaAdvance, self.direction))

class Camera:
    detailedBrightnessMap = "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~i!lI;:,\"^`. "
    simpleBrightnessMap = "@%#*+=-:."

    def __init__(self, c:Vector, n:Vector, res: int, rDA:float, rCT:float, rMD:float, dBM:str):
        self.c = c # camera position
        self.n = n # camera direction
        self.res = res # resolution, # of rays cast is proportional to resolution
        self.rDA = rDA # ray deltaAdvance
        self.rCT = rCT # ray collision tolerance
        self.rMD = rMD # raycast max depth
        self.dBM = dBM # one of this class' ascending brightness map strings, or a custom user-provided one

    def moveCameraPosBy(self, d:Vector):
        self.c = Vector.add(self.c, d)

    # assumes this Camera's direction in in R^3
    def getOrthonormalBasisForViewport(self) -> list[Vector]:
        basis:list[Vector] = [] 

        # can generalize this to higher dimensions later
        # finding 2 lin. indep. vectors in nullspace of [---n---], those lin. indep. vectors span (Span{n})^perp

        # print(f'{self.n=}')

        indexesOfFreeVariables = []
        indexOfPivot = 0
        alreadyFoundPivot = False
        for i in range(len(self.n)):
            if self.n[i] == 0 or alreadyFoundPivot:
                indexesOfFreeVariables.append(i)

            if self.n[i] != 0 and not alreadyFoundPivot:
                alreadyFoundPivot = True
                indexOfPivot = i

        for x2, x3 in ((0, 1), (1, 0)):
            n0 = self.n[indexOfPivot]
            x1 = -self.n[indexesOfFreeVariables[0]]/n0 * x2 + -self.n[indexesOfFreeVariables[1]]/n0 * x3
            
            vL = [0, 0, 0]
            vL[indexOfPivot] = x1
            vL[indexesOfFreeVariables[0]] = x2
            vL[indexesOfFreeVariables[1]] = x3
            basis.append(Vector(vL))

        # print(f'{basis=}')

        #Performing Gram-Schmidt on the 2 lin. indep. basis vectors for the viewport's subspace found in the previous step
        basis[1] = Vector.subtract(basis[1], 
            Vector.scalar_multiply(Vector.dot_product(basis[1],basis[0]) / Vector.dot_product(basis[0], basis[0]), basis[0]))

        basis[0] = Vector.normalize(basis[0])
        basis[1] = Vector.normalize(basis[1])
        return basis

    # assumes rays are in R^3
    def generateRays(self, oB:list[Vector]) -> list[Ray]:
        rays:list[Ray] = []
        for i in range(0, self.res):
            for j in range(0, self.res):
                rayOffsetV0 = Vector.scalar_multiply((i - self.res/2), oB[0]) 
                rayOffsetV1 = Vector.scalar_multiply((j - self.res/2), oB[1]) 
                rays.append(Ray(Vector.add(Vector.add(self.c, rayOffsetV0), rayOffsetV1), self.n, self.rDA))
        return rays

    def castRays(self, rays:list[Ray]):
        while len(rays) > 0:
            for currRay in rays[:]:
                currRay.advance()

                if currRay.length() >= self.rMD:
                    rays.remove(currRay)
                    continue

                for renderable in RenderableManager.renderables:
                    if renderable.collides(currRay.currPos, self.rCT):
                        rays.remove(currRay)
                        break

    def renderFrame(self) -> list[list[str]]:
        oB = self.getOrthonormalBasisForViewport()
        rays = self.generateRays(oB)
        self.castRays(rays[:]) # this function changes the ray objects themselves

        # because of the particular order in which I am raycasting, I know that each ray is listed in top-bottom, left-right order
        # therefore I can generate a frame using that knowledge (rather than any explicit projections) 

        # this can be thought of as an implicit projection onto the viewport because of the following: 
        # orthogonal decomposition theorem states that y = yhat + z where y is in V, yhat is in W, and z is in W perp
        # in this case, we have y (the ray endPos) and z (ray endPos - ray startPos)
        # endPos = yhat + (endPos - startPos) -> yhat = startPos 

        frame = []
        for i in range(self.res):
            currLine:list[str] = []
            for j in range(self.res):
                # probably the single most devious line of the whole program, it does the following
                # 1. Maps the current i and j into a single number representing the index of a specific ray in rays
                # 2. Gets the length of that ray and divides it by rayMaxDepth (max ray length) to get a float from [0,1] 
                # 3. Maps that float to an int between [0, len(self.aBM)]
                # 4. Maps that int to an int between [-1, len(self.aBM)-1]
                # 5. Maps that int to an int between [0, len(self.aBM)-1] 
                # Step 5 is because super close things should be very light (earlier in aBM), not very dark (later in aBM)
                currLine.append(self.dBM[max(0, ((int) (rays[i*self.res + j].length()/self.rMD*len(self.dBM)))-1)])
            frame.append(currLine)
        return frame
    
    def drawFrame(self):
        for row in self.renderFrame():
            thisRow = ""
            for col in row:
                thisRow += f" {col} "
            print(thisRow)

if __name__ == "__main__":
    camera = Camera(Vector([0,0,-5]), Vector([0,0,1]), 20, 0.1, 0.35, 3, Camera.simpleBrightnessMap)
    a = RenderableDisk(Vector([0, 0, 2]), Vector([0, 0, 1]), 10)

    # while (True):
    #     camera.drawFrame()
    #     cameraDeltaPos = [float(s) for s in input("Provide 3 numbers to move around (space seperated): ").split(" ")]
    #     camera.moveCameraPosBy(Vector(cameraDeltaPos))

    while (True):
        print("\n\n\n\n\n\n\n\n")
        camera.drawFrame()
        a.rotate(5, Vector([0, 1, 0]))
        sleep(0.05)
