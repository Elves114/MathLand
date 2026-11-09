"""Testes da API Flask (test_client)."""

import json


def test_get_operations_catalogo(client):
    response = client.get("/api/operations")
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload["categories"]) == 16
    assert len(payload["operations"]) == 72

    # cada operação referenciada tem de pertencer a uma categoria existente
    category_ids = {category["id"] for category in payload["categories"]}
    for operation in payload["operations"]:
        assert operation["category"] in category_ids
        assert operation["fields"], f"{operation['id']} sem campos"


def test_post_calculate_sucesso(client):
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "arit.soma", "inputs": {"a": "2", "b": "3"}}),
        content_type="application/json",
    )
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["result"]["display"] == "2 + 3 = 5"
    assert payload["operation"]["id"] == "arit.soma"


def test_post_calculate_converte_virgula_decimal(client):
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "arit.soma", "inputs": {"a": "12,5", "b": "7"}}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["result"]["display"] == "12.5 + 7 = 19.5"


def test_post_calculate_operacao_desconhecida(client):
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "nao.existe", "inputs": {}}),
        content_type="application/json",
    )
    assert response.status_code == 404
    assert response.get_json()["ok"] is False


def test_post_calculate_campo_em_falta(client):
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "arit.soma", "inputs": {"a": "2"}}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "obrigatório" in response.get_json()["error"] or "vazio" in response.get_json()["error"]


def test_post_calculate_valor_invalido(client):
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "arit.soma", "inputs": {"a": "abc", "b": "3"}}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_post_calculate_erro_de_dominio(client):
    """Erro de domínio (OpError) vira 400 com mensagem amigável."""
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "arit.divisao", "inputs": {"a": "10", "b": "0"}}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "zero" in response.get_json()["error"]


def test_post_calculate_id_legado(client):
    """O id antigo 'frac_para_decimal' continua a ser aceite (compatibilidade)."""
    response = client.post(
        "/api/calculate",
        data=json.dumps({"id": "frac_para_decimal", "inputs": {"a": "5/8"}}),
        content_type="application/json",
    )
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["ok"] is True
    # o catálogo/resposta usa o id novo canónico
    assert payload["operation"]["id"] == "frac.para_decimal"
    assert payload["result"]["display"] == "5/8 = 0.625"


def test_get_api_desconhecida(client):
    response = client.get("/api/inexistente")
    assert response.status_code == 404
    assert response.get_json()["ok"] is False


def test_get_index_serve_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MathLab" in response.data


def test_get_ficheiro_frontend(client):
    response = client.get("/app.js")
    assert response.status_code == 200
