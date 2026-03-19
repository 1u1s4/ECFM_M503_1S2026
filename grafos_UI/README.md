# Grafos UI

Visualizador concurrente de BFS, DFS, Dijkstra y Random Walk sobre una retícula cuadrada generada a partir de `N` y `D`.

## Requisitos

- Python 3.11+
- `pip install -r requirements.txt`

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 grafos_UI/main.py
```

O entrando al proyecto:

```bash
cd grafos_UI
python3 main.py
```

## Probar

Las pruebas están escritas con `unittest` y también corren con `pytest`.

```bash
python3 -m unittest discover -s grafos_UI/tests
```
