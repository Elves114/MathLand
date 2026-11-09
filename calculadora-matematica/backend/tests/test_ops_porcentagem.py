"""Testes unitários das operações de porcentagem."""

import pytest

from ops.helpers import OpError


def test_percentagem_de_valor(run_op):
    assert (
        run_op("pct.valor", percent=20, value=150)["display"]
        == "20% de 150 = 30"
    )


def test_aumento(run_op):
    assert (
        run_op("pct.aumento", value=250, percent=23)["display"]
        == "250 com aumento de 23% = 307.5"
    )


def test_desconto(run_op):
    assert (
        run_op("pct.desconto", value=250, percent=15)["display"]
        == "250 com desconto de 15% = 212.5"
    )


def test_desconto_acima_de_100(run_op):
    with pytest.raises(OpError, match="0% e 100%"):
        run_op("pct.desconto", value=250, percent=150)


def test_que_percentagem(run_op):
    assert run_op("pct.taxa", part=30, whole=150)["display"] == "30 é 20% de 150"


def test_que_percentagem_total_zero(run_op):
    with pytest.raises(OpError):
        run_op("pct.taxa", part=30, whole=0)


def test_variacao_crescimento(run_op):
    assert (
        run_op("pct.variacao", from_value=80, to_value=100)["display"]
        == "De 80 para 100: aumento de 25%"
    )


def test_variacao_descida(run_op):
    assert (
        run_op("pct.variacao", from_value=100, to_value=80)["display"]
        == "De 100 para 80: descida de 20%"
    )


def test_variacao_inicial_zero(run_op):
    with pytest.raises(OpError):
        run_op("pct.variacao", from_value=0, to_value=10)
