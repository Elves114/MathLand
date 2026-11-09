"""Testes unitários das operações com frações."""

import pytest
from fractions import Fraction

from ops.helpers import OpError, decimal_places, parse_fraction


def test_soma(run_op):
    assert run_op("frac.soma", a="1/2", b="1/3")["display"] == "1/2 + 1/3 = 5/6"


def test_subtracao(run_op):
    assert run_op("frac.subtracao", a="3/4", b="1/6")["display"] == "3/4 − 1/6 = 7/12"


def test_multiplicacao(run_op):
    assert (
        run_op("frac.multiplicacao", a="2/3", b="5/7")["display"]
        == "2/3 × 5/7 = 10/21"
    )


def test_divisao(run_op):
    assert run_op("frac.divisao", a="3/5", b="2/9")["display"] == "3/5 ÷ 2/9 = 27/10"


def test_divisao_por_zero(run_op):
    with pytest.raises(OpError):
        run_op("frac.divisao", a="3/5", b="0")


def test_simplificar(run_op):
    assert (
        run_op("frac.simplificar", value="36/48")["display"] == "36/48 = 3/4 ≈ 0.75"
    )


def test_decimal_para_fracao(run_op):
    assert run_op("frac.decimal_para_fracao", value="0.75")["display"] == "0.75 = 3/4"


def test_para_decimal(run_op):
    assert run_op("frac.para_decimal", a="5/8")["display"] == "5/8 = 0.625"


def test_numero_misto(run_op):
    assert run_op("frac.misto", value="2 3/4")["display"] == "2 + 3/4 = 11/4"


# ------------------------------------------------- validação (casos-limite)


def test_denominador_zero_lanca_operror():
    """'1/0' levanta ZeroDivisionError no Fraction — tem de virar OpError amigável."""
    with pytest.raises(OpError, match="denominador"):
        parse_fraction("1/0")


def test_fracao_mal_formada():
    with pytest.raises(OpError):
        parse_fraction("abc")


def test_denominador_vazio():
    with pytest.raises(OpError):
        parse_fraction("3/")


def test_decimal_places_notacao_cientifica():
    """str(1e-05) é '1e-05' — a contagem tem de dar 5, não 0."""
    assert decimal_places(1e-05) == 5
    assert decimal_places(0.25) == 2
    assert decimal_places(48) == 0
    assert decimal_places(Fraction(3, 4)) == 2
    assert decimal_places(Fraction(7, 3)) > 0  # decimal infinito não rebenta


def test_id_frac_para_decimal_segue_o_padrao():
    """IDs seguem o padrão categoria.acao (regressão do id 'frac_para_decimal')."""
    from ops.registry import OPERATIONS

    assert "frac.para_decimal" in OPERATIONS
    assert "frac_para_decimal" not in OPERATIONS
