import time
import torch
import numpy as np

# ===== CONFIGURACIÓN =====
N = 100_000  # Tamaño del array
A = range(N)

# Detectar si MPS (Metal Performance Shaders) está disponible
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"🖥️  Dispositivo detectado: {device}")
if device.type == "mps":
    print("✅ GPU M2 disponible - usando Metal Performance Shaders")
else:
    print("⚠️  GPU no disponible - usando CPU")

print(f"Comparación de algoritmos con n={N}")
print("=" * 60)

# ===== VERSIÓN 1: O(n²) - Original (Fuerza bruta) =====
print("\n1️⃣  VERSIÓN O(n²) - Doble bucle")
inicio = time.perf_counter()

S1 = 0
for i in A:  # n operaciones
    for j in A:  # n operaciones cada una
        S1 += i + j

tiempo_1 = time.perf_counter() - inicio
print(f"   Resultado: {S1:,}")
print(f"   Tiempo: {tiempo_1:.6f} segundos")
print(f"   Complejidad: n² = {N}² = {N**2:,} operaciones")


# ===== VERSIÓN 1B: O(n²) en GPU M2 con PyTorch + MPS =====
print("\n1️⃣B VERSIÓN O(n²) - GPU M2 (Metal Performance Shaders)")
inicio = time.perf_counter()

# Convertir a tensor de PyTorch y mover a GPU
A_tensor = torch.arange(N, dtype=torch.float32, device=device)

# Crear matriz de broadcast: [N, 1] + [1, N] = [N, N]
# Esto calcula todas las sumas i+j en paralelo en la GPU
inicio_gpu = time.perf_counter()
A_col = A_tensor.view(-1, 1)  # [N, 1]
A_row = A_tensor.view(1, -1)  # [1, N]
matriz_sumas = A_col + A_row  # [N, N] - broadcasting automático

# Sumar todos los elementos
S1b = matriz_sumas.sum().item()

tiempo_1b = time.perf_counter() - inicio
print(f"   Resultado: {int(S1b):,}")
print(f"   Tiempo: {tiempo_1b:.6f} segundos")
print(f"   Complejidad: n² operaciones en paralelo (GPU)")
print(f"   💡 Ventaja: Paralelización masiva en GPU")


# ===== VERSIÓN 2: O(n) - Precálculo de suma =====
print("\n2️⃣  VERSIÓN O(n) - Precálculo de suma")
inicio = time.perf_counter()

n = len(A)
suma_A = sum(A)  # O(n) - calcular una vez

S2 = 0
for i in A:  # n operaciones
    # Por cada i, sumamos: i*n + suma_A
    # Esto equivale a: (i+0) + (i+1) + (i+2) + ... + (i+(n-1))
    S2 += n * i + suma_A

tiempo_2 = time.perf_counter() - inicio
print(f"   Resultado: {S2:,}")
print(f"   Tiempo: {tiempo_2:.6f} segundos")
print(f"   Complejidad: n = {N:,} operaciones")


# ===== VERSIÓN 3: O(1) - Fórmula matemática =====
print("\n3️⃣  VERSIÓN O(1) - Fórmula matemática directa")
inicio = time.perf_counter()

n = len(A)
# Fórmula: S = 2n × suma(A)
# Para range(n): suma(0..n-1) = n(n-1)/2
suma_A = n * (n - 1) // 2
S3 = 2 * n * suma_A

tiempo_3 = time.perf_counter() - inicio
print(f"   Resultado: {S3:,}")
print(f"   Tiempo: {tiempo_3:.6f} segundos")
print(f"   Complejidad: O(1) - operaciones constantes")


# ===== COMPARACIÓN FINAL =====
print("\n" + "=" * 60)
print("📊 COMPARACIÓN DE RENDIMIENTO:")
print("=" * 60)
print(f"CPU O(n²):  {tiempo_1:.6f}s  {'✓ Correcto' if abs(S1 - S2) < 1 else '✗ Error'}")
print(f"GPU O(n²):  {tiempo_1b:.6f}s  (×{tiempo_1/tiempo_1b:.1f} vs CPU)")
print(f"CPU O(n):   {tiempo_2:.6f}s  (×{tiempo_1/tiempo_2:.1f} más rápido)")
print(f"O(1):       {tiempo_3:.6f}s  (×{tiempo_1/tiempo_3:.1f} más rápido)")
print("=" * 60)

# Verificación (permitiendo pequeñas diferencias por precisión float)
tolerancia = 1e-3
resultado_correcto = (
    abs(S1 - S2) < tolerancia and 
    abs(S1 - S3) < tolerancia and 
    abs(S1 - int(S1b)) < tolerancia
)
if resultado_correcto:
    print("✅ Todos los resultados coinciden")
else:
    print(f"⚠️  Pequeñas diferencias por precisión numérica")
    print(f"   S1 (CPU O(n²)): {S1}")
    print(f"   S1b (GPU O(n²)): {int(S1b)}")
    print(f"   S2 (O(n)): {S2}")
    print(f"   S3 (O(1)): {S3}")

print(f"\n💡 Nota: La GPU M2 es mejor para operaciones más grandes (N > 10,000)")
print(f"   Con n={N:,}, la transferencia de datos puede dominar el tiempo total")
