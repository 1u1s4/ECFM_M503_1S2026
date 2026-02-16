"""Cargar chistes desde JSON e indexarlos en ChromaDB."""

import json
from pathlib import Path

import chromadb

DB_PATH = Path(__file__).parent / "chroma_data"
JOKES_FILE = Path(__file__).parent / "jokes.json"
COLLECTION_NAME = "chistes"


def extract_joke_text(data: dict) -> str | None:
    """Extrae el texto del chiste (single o twopart)."""
    if data.get("type") == "single":
        return data.get("joke")
    if data.get("type") == "twopart":
        setup = data.get("setup", "")
        delivery = data.get("delivery", "")
        return f"{setup} {delivery}".strip() if setup or delivery else None
    return None


def main() -> None:
    if not JOKES_FILE.exists():
        print(f"Error: No existe {JOKES_FILE}. Ejecuta primero fetch_jokes.py")
        return

    with open(JOKES_FILE, encoding="utf-8") as f:
        raw_jokes = json.load(f)

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for i, data in enumerate(raw_jokes):
        text = extract_joke_text(data)
        if text:
            documents.append(text)
            metadatas.append({
                "category": data.get("category", ""),
                "type": data.get("type", ""),
                "id_api": str(data.get("id", i)),
            })
            ids.append(f"joke_{i}")

    if not documents:
        print("No se encontraron chistes validos en el JSON.")
        return

    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Reemplazar coleccion si ya existia (para re-ingesta)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"Indexados {len(documents)} chistes en ChromaDB")
    print(f"Ruta: {DB_PATH.resolve()}")
    print(f"Coleccion: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
