"""Testes unitários das operações de estatística."""

import pytest

from ops.helpers import OpError


def test_estatisticas_descritivas(run_op, detalhe):
    # Dados: 4, 8, 6, 4, 2, 9, 4  (n = 7, Σx = 37)
    resultado = run_op("est.descritivas", valores=[4, 8, 6, 4, 2, 9, 4])
    assert float(detalhe(resultado, "Média")) == pytest.approx(37 / 7, abs=1e-6)
    assert float(detalhe(resultado, "Mediana")) == pytest.approx(4)
    assert detalhe(resultado, "Moda") == "4"
    assert float(detalhe(resultado, "Amplitude")) == pytest.approx(7)
    # σ² = Σ(x − x̄)² ÷ n = 37.428571… ÷ 7
    assert float(detalhe(resultado, "Variância (σ²)")) == pytest.approx(5.346939, abs=1e-5)
    assert float(detalhe(resultado, "Desvio padrão (σ)")) == pytest.approx(2.312345, abs=1e-5)


def test_estatisticas_uma_sola_entrada(run_op):
    with pytest.raises(OpError, match="pelo menos 2 valores"):
        run_op("est.descritivas", valores=[5])


def test_estatisticas_sem_moda(run_op, detalhe):
    resultado = run_op("est.descritivas", valores=[1, 2, 3])
    assert "sem moda" in detalhe(resultado, "Moda")


def test_estatisticas_duas_marcas_de_moda(run_op, detalhe):
    resultado = run_op("est.descritivas", valores=[1, 1, 2, 2, 3])
    assert detalhe(resultado, "Moda") == "1, 2"


def test_media_ponderada(run_op, detalhe):
    # (16×6 + 14×4 + 12×2) ÷ 12 = 176 ÷ 12
    resultado = run_op("est.ponderada", valores=[16, 14, 12], pesos=[6, 4, 2])
    assert float(detalhe(resultado, "Média ponderada")) == pytest.approx(176 / 12, abs=1e-6)


def test_media_ponderada_quantidades_diferentes(run_op):
    with pytest.raises(OpError, match="mesma quantidade"):
        run_op("est.ponderada", valores=[16, 14], pesos=[6, 4, 2])


def test_media_ponderada_pesos_negativos(run_op):
    with pytest.raises(OpError, match="negativos"):
        run_op("est.ponderada", valores=[16, 14], pesos=[-1, 2])


def test_media_ponderada_soma_zero(run_op):
    with pytest.raises(OpError, match="soma dos pesos"):
        run_op("est.ponderada", valores=[16, 14], pesos=[0, 0])
