"""Testes unitários das operações sobre números."""

import pytest

from ops.helpers import OpError


def test_mdc(run_op):
    assert run_op("num.mdc", a=48, b=18)["display"] == "MDC(48, 18) = 6"


def test_mdc_primos_entre_si(run_op):
    resultado = run_op("num.mdc", a=7, b=13)
    assert resultado["display"] == "MDC(7, 13) = 1"
    assert any("primos entre si" in step for step in resultado["steps"])


def test_mmc(run_op):
    assert run_op("num.mmc", a=48, b=18)["display"] == "MMC(48, 18) = 144"


def test_mmc_com_zero(run_op):
    assert run_op("num.mmc", a=48, b=0)["display"] == "MMC(48, 0) = 0"


def test_primo_verdadeiro(run_op):
    assert run_op("num.primo", n=97)["display"] == "97 é primo ✓"


def test_primo_falso(run_op):
    resultado = run_op("num.primo", n=91)
    assert resultado["display"] == "91 não é primo (divisível por 7)."


def test_primo_menor_que_dois(run_op):
    assert "não é primo" in run_op("num.primo", n=1)["display"]


def test_fatoracao(run_op):
    assert run_op("num.fatoracao", n=360)["display"] == "360 = 2³ × 3² × 5"


def test_fatoracao_unidade(run_op):
    assert run_op("num.fatoracao", n=1)["display"].startswith("1 = 1")


def test_fatoracao_invalida(run_op):
    with pytest.raises(OpError, match="≥ 1"):
        run_op("num.fatoracao", n=0)


def test_analise_numero(run_op, detalhe):
    resultado = run_op("num.analise", n=2340)
    assert resultado["display"] == "2340: par, 4 dígitos, soma = 9"
    assert detalhe(resultado, "Paridade") == "par"
    assert detalhe(resultado, "Divisível por 3") == "sim"
    assert detalhe(resultado, "Divisível por 5") == "sim"


def test_conversao_de_bases(run_op):
    resultado = run_op("num.bases", value="1011", from_base="2", to_base="10")
    assert "1011₂ = 11₁₀" in resultado["display"]
    assert "(decimal: 11)" in resultado["display"]


def test_conversao_hexadecimal(run_op, detalhe):
    resultado = run_op("num.bases", value="FF", from_base="16", to_base="10")
    assert detalhe(resultado, "Valor decimal") == "255"


def test_conversao_digito_invalido(run_op):
    with pytest.raises(OpError, match="não é um número válido"):
        run_op("num.bases", value="1012", from_base="2", to_base="10")
