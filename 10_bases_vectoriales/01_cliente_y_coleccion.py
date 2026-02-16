"""Ejemplo 1: crear cliente y coleccion en memoria."""

import chromadb


def main() -> None:
    client = chromadb.Client()

    collection = client.get_or_create_collection(
        name="mis_documentos",
        metadata={"hnsw:space": "cosine"},
    )

    print("Coleccion lista:", collection.name)
    print("Metadata:", collection.metadata)


if __name__ == "__main__":
    main()
