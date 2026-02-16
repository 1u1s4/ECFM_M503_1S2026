"""Ejemplo 2: operaciones CRUD basicas y busqueda semantica."""

from chromadb.api.types import Document


import chromadb


COLLECTION_NAME = "mis_documentos_crud"


def reset_collection(client: chromadb.ClientAPI, name: str):
    try:
        client.delete_collection(name=name)
    except Exception:
        pass
    return client.create_collection(name=name, metadata={"hnsw:space": "cosine"})


def main() -> None:
    client = chromadb.Client()
    collection = reset_collection(client, COLLECTION_NAME)

    collection.add(
        documents=[
            "Python es un lenguaje de programacion",
            "Machine learning usa algoritmos para aprender",
            "Las bases de datos almacenan informacion",
            "El AGI es el intelecto artificial general",
            "C++ es un lenguaje rapido y eficiente"
        ],
        metadatas=[{"tipo": "prog"}, {"tipo": "ia"}, {"tipo": "db"}, {"tipo": "ai"}, {"tipo": "prog"}],
        ids=["doc1", "doc2", "doc3", "doc4", "doc5"],
    )

    print(f"Documentos cargados: {collection.count()}")

    resultados = collection.query(
        query_texts=["inteligencia artificial"],
        n_results=2,
    )
    print("\nTop 2 para 'inteligencia artificial':")
    for i, doc in enumerate[Document](resultados["documents"][0], start=1):
        print(f"{i}. {doc}")

    resultados_filtrados = collection.query(
        query_texts=["codigo"],
        where={"tipo": "prog"},
        n_results=1,
    )
    print("\nBusqueda filtrada (tipo='prog'):")
    print(resultados_filtrados["documents"][0])


if __name__ == "__main__":
    main()
