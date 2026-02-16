"""Ejemplo 4: update, delete y filtros por metadatos."""

import chromadb


COLLECTION_NAME = "mis_documentos_mantenimiento"


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
            "TensorFlow sirve para deep learning",
            "NumPy ayuda con calculo numerico",
            "PostgreSQL gestiona datos relacionales",
        ],
        metadatas=[
            {"area": "ia", "nivel": "avanzado"},
            {"area": "python", "nivel": "basico"},
            {"area": "db", "nivel": "intermedio"},
        ],
        ids=["d1", "d2", "d3"],
    )

    collection.update(
        ids=["d2"],
        documents=["NumPy y pandas son clave para analisis de datos"],
        metadatas=[{"area": "python", "nivel": "intermedio"}],
    )

    docs_python = collection.get(where={"area": "python"})
    print("Registros con area='python':", docs_python["ids"])

    collection.delete(ids=["d1"])
    print("Total despues de eliminar d1:", collection.count())

    resultados = collection.query(
        query_texts=["analisis de datos con python"],
        where={"nivel": "intermedio"},
        n_results=2,
    )
    print("Resultados finales filtrados por nivel='intermedio':")
    for i, doc in enumerate(resultados["documents"][0], start=1):
        print(f"{i}. {doc}")


if __name__ == "__main__":
    main()
