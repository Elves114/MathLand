"""Testes unitários das operações de álgebra."""

import pytest

from ops.helpers import OpError


def test_equacao_linear(run_op):
    resultado = run_op("alg.linear", a=2, b=4, c=10)
    assert resultado["display"] == "2x + 4 = 10  →  x = 3"
    assert resultado["details"][0]["value"] == "x = 3"


def test_linear_sem_solucao(run_op):
    with pytest.raises(OpError, match="não tem solução"):
        run_op("alg.linear", a=0, b=3, c=4)


def test_linear_infinitas_solucoes(run_op):
    with pytest.raises(OpError, match="infinitas soluções"):
        run_op("alg.linear", a=0, b=3, c=3)


def test_quadratura_duas_raizes(run_op):
    resultado = run_op("alg.quadratica", a=1, b=-5, c=6)
    assert resultado["display"] == "Duas soluções reais: x₁ = 2  |  x₂ = 3"


def test_quadratica_delta_negativo_sem_verificacao_de_soma(run_op):
    """Com Δ < 0 não existem raízes reais → o passo "x₁ + x₂" não faz sentido."""
    resultado = run_op("alg.quadratica", a=1, b=2, c=5)
    assert "Sem raízes reais" in resultado["display"]
    assert not any("Verificação com a soma" in step for step in resultado["steps"])


def test_quadratica_delta_zero_com_verificacao(run_op):
    resultado = run_op("alg.quadratica", a=1, b=2, c=1)
    assert resultado["display"] == "Uma solução dupla: x = -1"
    assert any("Verificação com a soma" in step for step in resultado["steps"])


def test_quadratica_a_zero(run_op):
    with pytest.raises(OpError, match="1.º grau"):
        run_op("alg.quadratica", a=0, b=2, c=1)


def test_sistema_2x2(run_op):
    """Caso pedido na revisão: sistema_2x2(1,1,5,2,-1,1) → x=2, y=3."""
    resultado = run_op("alg.sistema", a1=1, b1=1, c1=5, a2=2, b2=-1, c2=1)
    assert resultado["display"] == "x = 2  |  y = 3"
    assert [item["value"] for item in resultado["details"]] == ["2", "3"]


def test_sistema_sem_solucao(run_op):
    with pytest.raises(OpError, match="não tem solução"):
        run_op("alg.sistema", a1=1, b1=1, c1=1, a2=1, b2=1, c2=2)


def test_sistema_infinitas_solucoes(run_op):
    with pytest.raises(OpError, match="infinitas soluções"):
        run_op("alg.sistema", a1=1, b1=1, c1=1, a2=2, b2=2, c2=2)


def test_calcular_funcao(run_op):
    resultado = run_op("alg.funcao", expression="x^2 + 3*x - 5", x=4)
    assert resultado["display"] == "f(4) = 23"
