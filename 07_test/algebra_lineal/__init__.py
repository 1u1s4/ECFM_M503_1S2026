"""
Paquete de álgebra lineal simple.

Incluye operaciones básicas con vectores y matrices,
además de algunas transformaciones lineales clásicas en 2D.
"""

from .vectores import (  # noqa: F401
    suma_vectores,
    resta_vectores,
    producto_escalar,
    norma_vector,
    multiplicar_vector_por_escalar,
)

from .matrices import (  # noqa: F401
    suma_matrices,
    resta_matrices,
    multiplicar_matriz_por_escalar,
    transpuesta,
    multiplicar_matriz_vector,
    multiplicar_matrices,
)

from .transformaciones import (  # noqa: F401
    matriz_rotacion_2d,
    matriz_reflexion_eje_x,
    matriz_reflexion_eje_y,
)

