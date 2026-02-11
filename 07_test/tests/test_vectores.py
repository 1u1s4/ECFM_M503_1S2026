import math

from algebra_lineal.vectores import (
    suma_vectores,
    resta_vectores,
    multiplicar_vector_por_escalar,
    producto_escalar,
    norma_vector,
)


def test_suma_vectores():
    assert suma_vectores([1, 2], [3, 4]) == [4, 6]


def test_suma_vectores_dimension_incorrecta():
    try:
        suma_vectores([1, 2], [1, 2, 3])
        assert False, "Debió lanzar ValueError por dimensiones distintas"
    except ValueError:
        assert True


def test_resta_vectores():
    assert resta_vectores([5, 4], [1, 2]) == [4, 2]


def test_multiplicar_vector_por_escalar():
    assert multiplicar_vector_por_escalar([1, -2, 3], 2) == [2, -4, 6]


def test_producto_escalar():
    assert producto_escalar([1, 2, 3], [4, 5, 6]) == 32


def test_norma_vector():
    v = [3, 4]
    assert math.isclose(norma_vector(v), 5.0)

