"""Testes unitários das operações de finanças (inclui validações novas)."""

import pytest

from ops.helpers import OpError


def test_juros_simples(run_op, detalhe):
    resultado = run_op("fin.simples", capital=1000, rate=5, time=3)
    # J = 1000 × 5% × 3 = 150  →  M = 1150
    assert resultado["display"] == "Montante = 1150  (Juros J = 150)"
    assert float(detalhe(resultado, "Montante")) == pytest.approx(1150)
    assert float(detalhe(resultado, "Juros")) == pytest.approx(150)


def test_juros_compostos(run_op, detalhe):
    resultado = run_op("fin.composto", capital=1000, rate=5, time=3)
    # M = 1000 × 1.05³ = 1157.625
    assert float(detalhe(resultado, "Montante")) == pytest.approx(1157.625)
    assert float(detalhe(resultado, "Juros acumulados")) == pytest.approx(157.625)


def test_tempo_negativo(run_op):
    with pytest.raises(OpError, match="tempo"):
        run_op("fin.simples", capital=1000, rate=5, time=-1)


def test_capital_negativo(run_op):
    """Capital negativo não faz sentido financeiro (item 6 da revisão)."""
    for op_id in ("fin.simples", "fin.composto"):
        with pytest.raises(OpError, match="capital"):
            run_op(op_id, capital=-500, rate=5, time=3)


def test_capital_zero_e_permitido(run_op, detalhe):
    resultado = run_op("fin.simples", capital=0, rate=5, time=3)
    assert float(detalhe(resultado, "Montante")) == pytest.approx(0)


def test_taxa_muito_negativa(run_op):
    """Taxa ≤ −100% daria montante negativo / base negativa na potência."""
    for op_id in ("fin.simples", "fin.composto"):
        with pytest.raises(OpError):
            run_op(op_id, capital=1000, rate=-100, time=3)
        with pytest.raises(OpError):
            run_op(op_id, capital=1000, rate=-150, time=3)


def test_taxa_absurda(run_op):
    with pytest.raises(OpError, match="taxa"):
        run_op("fin.composto", capital=1000, rate=50_000, time=3)


def test_taxa_negativa_razoavel_e_permitida(run_op, detalhe):
    """−50% é legitimo (ex.: desvalorização) — só os extremos são bloqueados."""
    resultado = run_op("fin.simples", capital=200, rate=-50, time=2)
    # J = 200 × (−0.5) × 2 = −200  →  M = 0
    assert float(detalhe(resultado, "Montante")) == pytest.approx(0)
