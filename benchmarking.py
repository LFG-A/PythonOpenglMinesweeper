import numpy as np
import time

def benchmark_cross_product():

    A=np.array([[1, 0, 0, -5],
                [0, 1, 0, -5],
                [0, 0, 1, -5],
                [0, 0, 0, 1]], dtype=np.float32)
    # Create large example vertices list
    vertices = []
    for iz in range(100):
        for iy in range(100):
            for ix in range(100):
                vertices.append(np.array([ix, iy, iz, 1], dtype=np.float32))

    times = {"(A * vertex)": [], "(A @ vertex)": [], "(np.dot(A, vertex))": [], "(A.dot(vertex))": []}
    runs = 3
    for i in range(runs):

        # Benchmark element-wise multiplication (for reference, not comparable)
        start_time = time.time()
        elementwise_product = []
        for vertex in vertices:
            elementwise_product.append(A * vertex)
        end_time = time.time()
        times["(A * vertex)"].append(end_time - start_time)
        print("Element-wise multiplication (A * vertex) time: {:.6f} seconds".format(end_time - start_time))

        # Benchmark matrix multiplication using @ operator
        start_time = time.time()
        matrix_product_at = []
        for vertex in vertices:
            elementwise_product.append(A @ vertex)
        end_time = time.time()
        times["(A @ vertex)"].append(end_time - start_time)
        print("Matrix multiplication (A @ vertex) time: {:.6f} seconds".format(end_time - start_time))

        # Benchmark matrix multiplication using np.dot
        start_time = time.time()
        matrix_product_dot = []
        for vertex in vertices:
            elementwise_product.append(np.dot(A, vertex))
        end_time = time.time()
        times["(np.dot(A, vertex))"].append(end_time - start_time)
        print("np calling Matrix multiplication (np.dot(A, vertex)) time: {:.6f} seconds".format(end_time - start_time))

        # Benchmark matrix multiplication using np.dot
        start_time = time.time()
        matrixcall_product_dot = []
        for vertex in vertices:
            elementwise_product.append(A.dot(vertex))
        end_time = time.time()
        times["(A.dot(vertex))"].append(end_time - start_time)
        print("Matrix calling multiplication (A.dot(vertex)) time: {:.6f} seconds".format(end_time - start_time))

    print("\nBenchmarking results:\n")
    print(f"{runs} runs of A x vertex for {len(vertices)} vertices...")

    vertex = np.array([0, 0, 0, 1], dtype=np.float32)
    print(f"{A} * {vertex} = {A * vertex}\n")
    print(f"{A} @ {vertex} = {A @ vertex}\n")
    print(f"np.dot({A}, {vertex}) = {np.dot(A, vertex)}\n")
    print(f"{A}.dot({vertex}) = {A.dot(vertex)}\n")

    for key, value in times.items():
        print(f"{key} average time: {(np.mean(value) / len(vertices)) * 1000000} µs.")


"""-----------------------------------------------------------------------------------------------------------------"""


def benchmark_normalizing_vec3():

    # Create large example vertices list
    vertices = []
    for iz in range(100):
        for iy in range(100):
            for ix in range(100):
                vertices.append(np.array([ix, iy, iz, 1], dtype=np.float32))

    times = {"(np.linalg.norm(vertex))": [], "(np.sqrt(vertex.dot(vertex)))": []}
    runs = 3
    for i in range(runs):

        # Benchmark np.linalg.norm(vertex)
        start_time = time.time()
        linalg = []
        for vertex in vertices:
            linalg.append(np.linalg.norm(vertex))
        end_time = time.time()
        times["(np.linalg.norm(vertex))"].append(end_time - start_time)
        print("np.linalg.norm(vertex) time: {:.6f} seconds".format(end_time - start_time))

        # Benchmark np.sqrt(vertex.dot(vertex))
        start_time = time.time()
        dot = []
        for vertex in vertices:
            dot.append(np.sqrt(vertex.dot(vertex)))
        end_time = time.time()
        times["(np.sqrt(vertex.dot(vertex)))"].append(end_time - start_time)
        print("np.sqrt(vertex.dot(vertex)) time: {:.6f} seconds".format(end_time - start_time))

    print("\nBenchmarking results:\n")
    print(f"{runs} runs for {len(vertices)} vertices...")

    for key, value in times.items():
        print(f"{key} average time: {(np.mean(value) / len(vertices)) * 1000000} µs.")


"""-----------------------------------------------------------------------------------------------------------------"""


def benchmark_smaller_then():

    # Create large example vertices list
    vertices = []
    for iz in range(1000):
        vertices.append(np.random.uniform(-1, 1, 1))

    times = {"(vertex < 0)": [], "(vertex <= 0)": []}
    runs = 50
    for i in range(runs):

        # Benchmark (vertex < 0)
        start_time = time.time()
        erg = []
        for vertex in vertices:
            erg.append((vertex < 0))
        end_time = time.time()
        times["(vertex < 0)"].append(end_time - start_time)
        print("(vertex < 0) time: {:.6f} seconds".format(end_time - start_time))

        # Benchmark (vertex <= 0)
        start_time = time.time()
        erg2 = []
        for vertex in vertices:
            erg2.append((vertex <= 0))
        end_time = time.time()
        times["(vertex <= 0)"].append(end_time - start_time)
        print("(vertex <= 0) time: {:.6f} seconds".format(end_time - start_time))

    print("\nBenchmarking results:\n")
    print(f"{runs} runs for {len(vertices)} vertices...")

    for key, value in times.items():
        print(f"{key} average time: {(np.mean(value) / len(vertices)) * 1000000} µs.")



if __name__ == "__main__":

    # benchmark_cross_product()

    # benchmark_normalizing_vec3()

    benchmark_smaller_then()
