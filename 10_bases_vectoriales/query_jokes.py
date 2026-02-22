"""Busqueda semantica en la base de chistes."""

import sys
from pathlib import Path

import chromadb

DB_PATH = Path(__file__).parent / "chroma_data"
COLLECTION_NAME = "chistes"


def main() -> None:
    if not DB_PATH.exists():
        print(f"Error: No existe {DB_PATH}. Ejecuta primero fetch_jokes.py e ingest_jokes.py")
        return

    client = chromadb.PersistentClient(path=str(DB_PATH))

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        print(f"Error: Coleccion '{COLLECTION_NAME}' no encontrada. Ejecuta ingest_jokes.py")
        return

    query = "numerico"
    n_results = 1

    resultados = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )

    print(f"\nBusqueda: \"{query}\"\n")
    docs = resultados["documents"][0]
    metas = resultados["metadatas"][0] or [{}] * len(docs)

    for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
        cat = meta.get("category", "")
        print(f"{i}. [{cat}] {doc}\n")


if __name__ == "__main__":
    main()
