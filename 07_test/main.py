"""
Ejemplos de uso de la librería de álgebra lineal localizada en 07_test/algebra_lineal.

Puedes ejecutar este archivo directamente con:

    python main.py
"""

from algebra_lineal import (
    suma_vectores,
    multiplicar_vector_por_escalar,
    matriz_rotacion_2d,
)
from algebra_lineal.matrices import multiplicar_matriz_vector


def main() -> None:
    v1 = [1.0, 2.0]
    v2 = [3.0, 4.0]
    print("v1 + v2 =", suma_vectores(v1, v2))

    v3 = multiplicar_vector_por_escalar(v1, 2.0)
    print("2 * v1 =", v3)

    # Rotación de 90 grados (pi/2 radianes)
    import math

    r = matriz_rotacion_2d(math.pi / 2)
    v = [1.0, 0.0]
    print("Rotación de (1,0) 90°:", multiplicar_matriz_vector(r, v))


if __name__ == "__main__":
    main()

