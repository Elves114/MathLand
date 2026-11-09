"""MathLab — backend Flask da calculadora de matemática.

Expõe:
  GET  /api/operations  → catálogo de categorias e operações (para o frontend)
  POST /api/calculate   → executa uma operação com os inputs do utilizador
  GET  /                → serve a aplicação frontal (HTML/CSS/JS)

Arranque:  python backend/app.py   (ou: flask --app backend/app.py run)
"""

import os
import sys

# Garante que o pacote `ops` é encontrado mesmo com `python backend/app.py`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory

import ops  # noqa: F401  — importa todos os módulos e regista as operações
from ops.helpers import OpError, coerce_field
from ops.registry import CATEGORIES, OPERATIONS, get_operation, sorted_operations

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=None)


def catalog_payload():
    """Catálogo completo para o frontend renderizar os formulários."""
    return {
        "categories": [
            {"id": category_id, "name": name, "description": description}
            for category_id, name, description in CATEGORIES
        ],
        "operations": [
            {
                "id": operation["id"],
                "category": operation["category"],
                "name": operation["name"],
                "description": operation["description"],
                "fields": operation["fields"],
            }
            for operation in sorted_operations()
        ],
    }


@app.get("/api/operations")
def list_operations():
    return jsonify(catalog_payload())


@app.post("/api/calculate")
def calculate():
    payload = request.get_json(silent=True) or {}
    operation_id = payload.get("id")
    inputs = payload.get("inputs") or {}

    operation = get_operation(operation_id)
    if operation is None:
        return jsonify({"ok": False, "error": f"Operação desconhecida: {operation_id}"}), 404

    try:
        kwargs = {
            field["name"]: coerce_field(field, inputs.get(field["name"], ""))
            for field in operation["fields"]
        }
        result = operation["fn"](**kwargs)
    except OpError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except TypeError as exc:
        return jsonify({"ok": False, "error": f"Parâmetros inválidos: {exc}"}), 400
    except Exception as exc:  # erro inesperado de domínio
        app.logger.exception("Erro inesperado em %s", operation_id)
        return jsonify({"ok": False, "error": f"Erro inesperado ao calcular: {exc}"}), 500

    if isinstance(result, str):
        result = {"display": result}

    return jsonify(
        {
            "ok": True,
            "operation": {"id": operation["id"], "name": operation["name"]},
            "result": {
                "display": result.get("display", ""),
                "steps": result.get("steps", []) or [],
                "details": result.get("details", []) or [],
            },
        }
    )


# ---------------------------------------------------------------- frontend


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Recurso não encontrado."}), 404
    return "Página não encontrada (404).", 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"ok": False, "error": "Erro interno no servidor."}), 500


if __name__ == "__main__":
    # Configuração por variáveis de ambiente (ver README):
    #   PORT=8080 HOST=0.0.0.0 FLASK_DEBUG=0 python backend/app.py
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in {"1", "true", "yes", "on"}

    print()
    print(f"  MathLab a correr em  http://127.0.0.1:{port}")
    if host in {"0.0.0.0", "::"}:
        print(f"  Disponível na rede local em  http://<IP desta máquina>:{port}")
    if debug:
        print("  Modo debug ATIVO (FLASK_DEBUG=1) — apenas para uso local, nunca em produção.")
    print(f"  Operações registadas: {len(OPERATIONS)}")
    print()
    app.run(host=host, port=port, debug=debug)
