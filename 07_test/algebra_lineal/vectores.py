"""
Operaciones básicas con vectores representados como listas de números.

Se evita usar librerías externas (como NumPy) para mantener
la implementación lo más didáctica posible.
"""

from math import sqrt
from typing import List

Vector = List[float]


def _validar_mismo_tamano(v1: Vector, v2: Vector) -> None:
    if len(v1) != len(v2):
        raise ValueError("Los vectores deben tener el mismo tamaño.")


def suma_vectores(v1: Vector, v2: Vector) -> Vector:
    """Suma dos vectores componente a componente."""
    _validar_mismo_tamano(v1, v2)
    return [a + b for a, b in zip(v1, v2)]


def resta_vectores(v1: Vector, v2: Vector) -> Vector:
    """Resta dos vectores componente a componente (v1 - v2)."""
    _validar_mismo_tamano(v1, v2)
    return [a - b for a, b in zip(v1, v2)]


def multiplicar_vector_por_escalar(v: Vector, escalar: float) -> Vector:
    """Multiplica un vector por un escalar."""
    return [escalar * x for x in v]


def producto_escalar(v1: Vector, v2: Vector) -> float:
    """Calcula el producto escalar de dos vectores."""
    _validar_mismo_tamano(v1, v2)
    return sum(a * b for a, b in zip(v1, v2))


def norma_vector(v: Vector) -> float:
    """Calcula la norma euclidiana (longitud) de un vector."""
    return sqrt(producto_escalar(v, v))

