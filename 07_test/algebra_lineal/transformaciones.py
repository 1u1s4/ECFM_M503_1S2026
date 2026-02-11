"""
Transformaciones lineales clásicas en R^2 representadas por matrices.

Todas las funciones devuelven matrices 2x2 que actúan sobre vectores columna
de la forma [x, y].
"""

from math import cos, sin
from typing import List

Matriz = List[List[float]]


def matriz_rotacion_2d(angulo_radianes: float) -> Matriz:
    """
    Devuelve la matriz de rotación en el plano para un ángulo dado (en radianes).

    R(θ) = [[ cosθ, -sinθ],
            [ sinθ,  cosθ]]
    """
    c = cos(angulo_radianes)
    s = sin(angulo_radianes)
    return [[c, -s], [s, c]]


def matriz_reflexion_eje_x() -> Matriz:
    """
    Reflexión respecto al eje X.

    (x, y) -> (x, -y)
    """
    return [[1.0, 0.0], [0.0, -1.0]]


def matriz_reflexion_eje_y() -> Matriz:
    """
    Reflexión respecto al eje Y.

    (x, y) -> (-x, y)
    """
    return [[-1.0, 0.0], [0.0, 1.0]]

