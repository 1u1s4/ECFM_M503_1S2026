import math

from algebra_lineal.matrices import multiplicar_matriz_vector
from algebra_lineal.transformaciones import (
    matriz_rotacion_2d,
    matriz_reflexion_eje_x,
    matriz_reflexion_eje_y,
)


def test_matriz_rotacion_2d_90_grados():
    angulo = math.pi / 2  # 90 grados
    r = matriz_rotacion_2d(angulo)
    v = [1.0, 0.0]  # eje x
    resultado = multiplicar_matriz_vector(r, v)
    # Debe aproximarse a (0, 1)
    assert math.isclose(resultado[0], 0.0, abs_tol=1e-9)
    assert math.isclose(resultado[1], 1.0, abs_tol=1e-9)


def test_reflexion_eje_x():
    m = matriz_reflexion_eje_x()
    v = [3.0, 4.0]
    resultado = multiplicar_matriz_vector(m, v)
    assert resultado == [3.0, -4.0]


def test_reflexion_eje_y():
    m = matriz_reflexion_eje_y()
    v = [3.0, 4.0]
    resultado = multiplicar_matriz_vector(m, v)
    assert resultado == [-3.0, 4.0]

