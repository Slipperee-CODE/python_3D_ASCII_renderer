from renderer import *

class TestVectorOperations:
    @staticmethod
    def test(u:Vector, v:Vector, c:float):
        print(f"{u=} {v=} {c=}")

        print(f"{Vector.add(u, v)=}")
        print(f"{Vector.subtract(u, v)=}")
        print(f"{Vector.vector_multiply(u, v)=}")
        print(f"{Vector.scalar_multiply(u, c)=}")
        print(f"{Vector.dot_product(u, v)=}")
        print(f"{Vector.length(u)=}")
        print(f"{Vector.normalize(u)=}")
        print(f"{Vector.length(Vector.normalize(u))=}")

    @staticmethod
    def testRandomVectors():
        print("Start of testRandomVectors")
        import random
        u = Vector([random.randint(-5, 5) for _ in range(3)])
        v = Vector([random.randint(-5, 5) for _ in range(3)])
        c = random.randint(0, 3)

        TestVectorOperations.test(u, v, c)
        print("End of testRandomVectors \n")

    @staticmethod
    def testLen1Vectors():
        print("Start of testLen1Vectors")
        u = Vector([sqrt(2)/2, sqrt(2)/2])
        v = Vector([1/sqrt(10), 3/sqrt(10)])
        c = 3

        TestVectorOperations.test(u, v, c)
        print("End of testLen1Vectors \n")

    @staticmethod
    def testOrthogonalVectors():
        print("Start of testOrthogonalVectors")
        u = Vector([-2, 1])
        v = Vector([1, 2])
        c = 4

        TestVectorOperations.test(u, v, c)
        print("End of testOrthogonalVectors \n")

    @staticmethod
    def runAllTests():
        TestVectorOperations.testRandomVectors()
        TestVectorOperations.testRandomVectors()
        TestVectorOperations.testRandomVectors()

        TestVectorOperations.testLen1Vectors()
        TestVectorOperations.testOrthogonalVectors() 

if __name__ == "__main__":
    TestVectorOperations.runAllTests()
