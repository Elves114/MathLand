"""Testes unitários das operações de aritmética."""

import pytest

from ops.helpers import OpError


def test_soma(run_op):
    assert run_op("arit.soma", a=12.5, b=7)["display"] == "12.5 + 7 = 19.5"


def test_subtracao(run_op):
    assert run_op("arit.subtracao", a=20, b=8)["display"] == "20 − 8 = 12"


def test_multiplicacao(run_op):
    assert run_op("arit.multiplicacao", a=6, b=4)["display"] == "6 × 4 = 24"


def test_divisao(run_op):
    assert run_op("arit.divisao", a=10, b=4)["display"] == "10 ÷ 4 = 2.5"


def test_divisao_por_zero(run_op):
    with pytest.raises(OpError, match="zero"):
        run_op("arit.divisao", a=10, b=0)


def test_potencia(run_op):
    assert run_op("arit.potencia", base=2, exp=10)["display"] == "2^10 = 1024"


def test_potencia_zero_com_expoente_negativo(run_op):
    with pytest.raises(OpError):
        run_op("arit.potencia", base=0, exp=-1)


def test_raiz_quadrada(run_op):
    assert run_op("arit.raiz", n=144)["display"] == "√144 = 12"


def test_raiz_de_numero_negativo(run_op):
    with pytest.raises(OpError):
        run_op("arit.raiz", n=-4)


def test_expressao(run_op):
    resultado = run_op("arit.expressao", expression="(3 + 5) * 2^3 / sqrt(16)")
    assert resultado["display"] == "(3 + 5) * 2^3 / sqrt(16) = 16"


def test_expressao_divisao_por_zero(run_op):
    with pytest.raises(OpError):
        run_op("arit.expressao", expression="1/0")


def test_expressao_nao_executa_codigo(run_op):
    """O avaliador é construído sobre `ast` — nunca executa código arbitrário."""
    with pytest.raises(OpError):
        run_op("arit.expressao", expression="__import__('os').system('ls')")


def test_campo_invalido_rejeitado(run_op):
    with pytest.raises(OpError):
        run_op("arit.soma", a="abc", b=1)
