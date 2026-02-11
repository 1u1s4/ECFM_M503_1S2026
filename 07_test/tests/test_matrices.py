from algebra_lineal.matrices import (
    suma_matrices,
    resta_matrices,
    multiplicar_matriz_por_escalar,
    transpuesta,
    multiplicar_matriz_vector,
    multiplicar_matrices,
)


def test_suma_matrices():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    assert suma_matrices(a, b) == [[6, 8], [10, 12]]


def test_suma_matrices_dimensiones_incorrectas():
    a = [[1, 2, 3]]
    b = [[1, 2]]
    try:
        suma_matrices(a, b)
        assert False, "Debió lanzar ValueError"
    except ValueError:
        assert True


def test_resta_matrices():
    a = [[5, 6], [7, 8]]
    b = [[1, 2], [3, 4]]
    assert resta_matrices(a, b) == [[4, 4], [4, 4]]


def test_multiplicar_matriz_por_escalar():
    a = [[1, -2], [0, 3]]
    assert multiplicar_matriz_por_escalar(a, 2) == [[2, -4], [0, 6]]


def test_transpuesta():
    a = [[1, 2, 3], [4, 5, 6]]
    assert transpuesta(a) == [[1, 4], [2, 5], [3, 6]]


def test_multiplicar_matriz_vector():
    a = [[1, 2], [3, 4]]
    v = [5, 6]
    assert multiplicar_matriz_vector(a, v) == [17, 39]


def test_multiplicar_matrices():
    a = [[1, 2, 3], [4, 5, 6]]
    b = [[7, 8], [9, 10], [11, 12]]
    # Resultado calculado a mano
    assert multiplicar_matrices(a, b) == [[58, 64], [139, 154]]

