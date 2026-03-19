from __future__ import annotations

import sys


def main() -> int:
    try:
        from grafos_ui.app import main as run_app
    except ModuleNotFoundError as exc:
        if exc.name == "PyQt6":
            print(
                "PyQt6 no está instalado. Ejecuta: "
                "pip install -r grafos_UI/requirements.txt "
                "o entra a grafos_UI y usa: pip install -r requirements.txt"
            )
            return 1
        raise
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
