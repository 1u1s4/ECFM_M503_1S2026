"""Obtener chistes de la API JokeAPI y guardarlos en JSON."""

import json
import time
from pathlib import Path

import requests

API_URL = "https://v2.jokeapi.dev/joke/Any?lang=es"
OUTPUT_FILE = Path(__file__).parent / "jokes.json"


def fetch_joke() -> dict | None:
    """Obtiene un chiste de la API."""
    try:
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            return None
        return data
    except Exception:
        return None


def extract_joke_text(data: dict) -> str | None:
    """Extrae el texto del chiste (single o twopart)."""
    if data.get("type") == "single":
        return data.get("joke")
    if data.get("type") == "twopart":
        setup = data.get("setup", "")
        delivery = data.get("delivery", "")
        return f"{setup} {delivery}".strip() if setup or delivery else None
    return None


def main(n: int = 100) -> None:
    jokes: list[dict] = []
    seen_texts: set[str] = set()

    print(f"Obteniendo {n} chistes de {API_URL}...")

    while len(jokes) < n:
        data = fetch_joke()
        if data:
            text = extract_joke_text(data)
            if text and text not in seen_texts:
                seen_texts.add(text)
                jokes.append(data)
                print(f"  [{len(jokes)}/{n}] OK")
        time.sleep(0.5)  # Evitar rate limiting

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(jokes, f, ensure_ascii=False, indent=2)

    print(f"\nGuardados {len(jokes)} chistes en {OUTPUT_FILE}")


if __name__ == "__main__":
    main(n=100)
