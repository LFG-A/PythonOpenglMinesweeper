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

if __name__ == "__main__":
    benchmark_cross_product()
