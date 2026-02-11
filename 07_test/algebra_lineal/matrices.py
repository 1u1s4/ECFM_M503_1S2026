"""
Operaciones básicas con matrices representadas como listas de listas.
"""

from typing import List, Tuple

Numero = float
Matriz = List[List[Numero]]
Vector = List[Numero]


def dimensiones(matriz: Matriz) -> Tuple[int, int]:
    """Devuelve (filas, columnas). Lanza ValueError si la matriz es inválida."""
    if not matriz or not isinstance(matriz, list):
        raise ValueError("La matriz debe ser una lista no vacía de filas.")
    filas = len(matriz)
    columnas = len(matriz[0])
    if columnas == 0:
        raise ValueError("La matriz no puede tener 0 columnas.")
    for fila in matriz:
        if len(fila) != columnas:
            raise ValueError("Todas las filas deben tener la misma longitud.")
    return filas, columnas


def suma_matrices(a: Matriz, b: Matriz) -> Matriz:
    """Suma de matrices del mismo tamaño."""
    fa, ca = dimensiones(a)
    fb, cb = dimensiones(b)
    if (fa, ca) != (fb, cb):
        raise ValueError("Las matrices deben tener las mismas dimensiones.")
    return [[a[i][j] + b[i][j] for j in range(ca)] for i in range(fa)]


def resta_matrices(a: Matriz, b: Matriz) -> Matriz:
    """Resta de matrices del mismo tamaño (a - b)."""
    fa, ca = dimensiones(a)
    fb, cb = dimensiones(b)
    if (fa, ca) != (fb, cb):
        raise ValueError("Las matrices deben tener las mismas dimensiones.")
    return [[a[i][j] - b[i][j] for j in range(ca)] for i in range(fa)]


def multiplicar_matriz_por_escalar(a: Matriz, escalar: Numero) -> Matriz:
    """Multiplica una matriz por un escalar."""
    filas, columnas = dimensiones(a)
    return [[escalar * a[i][j] for j in range(columnas)] for i in range(filas)]


def transpuesta(a: Matriz) -> Matriz:
    """Devuelve la matriz transpuesta."""
    filas, columnas = dimensiones(a)
    return [[a[i][j] for i in range(filas)] for j in range(columnas)]


def multiplicar_matriz_vector(a: Matriz, v: Vector) -> Vector:
    """Multiplica una matriz A (m x n) por un vector v (n)."""
    filas, columnas = dimensiones(a)
    if len(v) != columnas:
        raise ValueError("Dimensiones incompatibles entre matriz y vector.")
    return [sum(a[i][j] * v[j] for j in range(columnas)) for i in range(filas)]


def multiplicar_matrices(a: Matriz, b: Matriz) -> Matriz:
    """Multiplicación de matrices A (m x n) y B (n x p)."""
    fa, ca = dimensiones(a)
    fb, cb = dimensiones(b)
    if ca != fb:
        raise ValueError("Dimensiones incompatibles para la multiplicación.")
    # C = A * B -> tamaño (fa x cb)
    return [
        [sum(a[i][k] * b[k][j] for k in range(ca)) for j in range(cb)]
        for i in range(fa)
    ]

