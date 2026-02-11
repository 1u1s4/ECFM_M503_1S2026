"""
conftest.py — agrega la carpeta 07_test al sys.path para que pytest
pueda encontrar el paquete algebra_lineal sin necesidad de instalación.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
