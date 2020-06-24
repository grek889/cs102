import numpy

from ProcessPool import ProcessPool


def heavy_computation(data_chunk):
    matrix_A, matrix_B = data_chunk
    n, m = len(matrix_A), len(matrix_A[0])
    k, l = len(matrix_B), len(matrix_B[0])

    if m != k:
        raise Exception('Размеры матриц не подходят для перемножения')

    matrix_C = [[0 for i in range(l)] for i in range(n)]

    for i in range(n):
        for q in range(l):
            el = 0
            for j in range(m):
                el += matrix_A[i][j] * matrix_B[j][q]

            matrix_C[i][q] = el

    return matrix_C


if __name__ == '__main__':
    a = ProcessPool(1, 5, '1Gb')

    l = numpy.random.randn(10, 3)
    m = numpy.random.randn(3, 10)
    big_data = [(numpy.random.randn(100, 100), numpy.random.randn(100, 100)) for i in range(10)]

    result = a.map(heavy_computation, big_data)
