"""Testes unitários das operações de razão e proporção."""

import pytest

from ops.helpers import OpError


def test_razao_simples_inteiros(run_op, detalhe):
    resultado = run_op("raz.simples", a=48, b=18)
    assert resultado["display"] == "48 : 18 = 8 : 3"
    assert detalhe(resultado, "Razão") == "8 : 3"


def test_razao_simples_decimais(run_op, detalhe):
    resultado = run_op("raz.simples", a=0.5, b=1.5)
    assert detalhe(resultado, "Razão") == "1 : 3"


def test_razao_simples_notacao_cientifica(run_op, detalhe):
    """Regressão: str(1e-05) = '1e-05' quebrava a contagem de casas decimais."""
    resultado = run_op("raz.simples", a=1e-05, b=2e-05)
    assert detalhe(resultado, "Razão") == "1 : 2"


def test_razao_zero_sobre_zero(run_op):
    with pytest.raises(OpError):
        run_op("raz.simples", a=0, b=0)


def test_regra_de_tres(run_op):
    resultado = run_op("raz.regra3", a=3, b=12, c=7)
    assert resultado["display"] == "3 → 12  então  7 → 28"


def test_regra_de_tres_origem_zero(run_op):
    with pytest.raises(OpError, match="zero"):
        run_op("raz.regra3", a=0, b=12, c=7)


def test_escala_mapa_para_real(run_op):
    resultado = run_op("raz.escala", scale="1:50000", distance=4, direction="mapa_para_real")
    assert resultado["display"] == "4 no mapa = 200000 na realidade"


def test_escala_real_para_mapa(run_op):
    resultado = run_op("raz.escala", scale="1:50000", distance=200000, direction="real_para_mapa")
    assert resultado["display"] == "200000 na realidade = 4 no mapa"


def test_escala_formato_invalido(run_op):
    with pytest.raises(OpError, match="formato"):
        run_op("raz.escala", scale="50 mil", distance=4, direction="mapa_para_real")


def test_media_proporcional(run_op):
    # x = √(4 × 9) = √36 = 6
    resultado = run_op("raz.media_proporcional", a=4, b=9)
    assert resultado["details"][0]["value"] == "6"


def test_media_proporcional_produto_negativo(run_op):
    with pytest.raises(OpError, match="negativo"):
        run_op("raz.media_proporcional", a=-4, b=9)
