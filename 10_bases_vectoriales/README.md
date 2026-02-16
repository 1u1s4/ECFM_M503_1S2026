# Clase 10 - Bases Vectoriales (ChromaDB)

Ejemplos practicos para probar ChromaDB basados en la clase 10.

## 1) Instalacion

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Ejecutar ejemplos

Desde esta carpeta (`10_bases_vectoriales`):

```bash
python3 01_cliente_y_coleccion.py
python3 02_crud_y_busqueda.py
python3 03_persistencia_local.py
python3 04_update_delete_y_filtros.py
```

## Archivos

- `01_cliente_y_coleccion.py`: cliente en memoria y creacion de coleccion con metrica coseno.
- `02_crud_y_busqueda.py`: insercion de documentos y consultas semanticas.
- `03_persistencia_local.py`: uso de `PersistentClient` para guardar datos en disco.
- `04_update_delete_y_filtros.py`: update, delete y filtros por metadatos.

## Nota

La primera ejecucion puede tardar un poco mas porque ChromaDB descarga el modelo por defecto para embeddings.
