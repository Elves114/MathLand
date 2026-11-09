"""Fixtures partilhadas pelos testes do MathLab.

Correr a partir da raiz do projeto:

    pytest
"""

import os
import sys

BACKEND_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest  # noqa: E402

from ops.helpers import coerce_field  # noqa: E402
from ops.registry import OPERATIONS  # noqa: E402


@pytest.fixture(scope="session")
def app():
    """Aplicação Flask em modo de teste."""
    import app as app_module

    app_module.app.config["TESTING"] = True
    return app_module.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def run_op():
    """Executa uma operação pelo id, aplicando a mesma coerção da API."""

    def _run(op_id, **inputs):
        operation = OPERATIONS[op_id]
        kwargs = {
            field["name"]: coerce_field(field, inputs.get(field["name"], ""))
            for field in operation["fields"]
        }
        return operation["fn"](**kwargs)

    return _run


@pytest.fixture()
def detalhe():
    """Devolve o valor (string) de um detalhe do resultado."""

    def _detalhe(result, label):
        for item in result.get("details", []):
            if item["label"] == label:
                return item["value"]
        raise AssertionError(
            f"Detalhe '{label}' não encontrado. Disponíveis: "
            f"{[i['label'] for i in result.get('details', [])]}"
        )

    return _detalhe
