"""Ejemplo 3: persistencia local con ChromaDB."""

from pathlib import Path

import chromadb


DB_PATH = Path("chroma_data")
COLLECTION_NAME = "mis_documentos_persistentes"


def main() -> None:
    client = chromadb.PersistentClient(path=str(DB_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        collection.add(
            documents=[
                "PostgreSQL es una base de datos relacional",
                "ChromaDB es util para busqueda vectorial",
            ],
            metadatas=[{"origen": "sql"}, {"origen": "vector"}],
            ids=["p1", "p2"],
        )
        print("Se insertaron documentos iniciales.")
    else:
        print("La coleccion ya tenia datos.")

    print("Ruta de persistencia:", DB_PATH.resolve())
    print("Total de documentos:", collection.count())


if __name__ == "__main__":
    main()
