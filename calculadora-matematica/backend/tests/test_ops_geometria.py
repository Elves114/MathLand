"""Testes unitários das operações de geometria (inclui casos-limite)."""

import pytest

from ops.helpers import OpError


def test_retangulo(run_op, detalhe):
    resultado = run_op("geo.retangulo", base=8, altura=5)
    assert "Área = 40" in resultado["display"]
    assert "Perímetro = 26" in resultado["display"]
    assert float(detalhe(resultado, "Área")) == pytest.approx(40)
    assert float(detalhe(resultado, "Perímetro")) == pytest.approx(26)
    assert float(detalhe(resultado, "Diagonal")) == pytest.approx(9.433981, abs=1e-5)


def test_retangulo_dimensao_invalida(run_op):
    """Casos-limite: dimensão zero ou negativa não forma retângulo."""
    with pytest.raises(OpError, match="positivo"):
        run_op("geo.retangulo", base=0, altura=5)
    with pytest.raises(OpError, match="positivo"):
        run_op("geo.retangulo", base=-3, altura=5)


def test_quadrado_lado_negativo(run_op):
    with pytest.raises(OpError, match="positivo"):
        run_op("geo.quadrado", lado=-6)


def test_triangulo_tres_lados(run_op, detalhe):
    resultado = run_op("geo.triangulo_lados", a=7, b=8, c=9)
    assert float(detalhe(resultado, "Perímetro")) == pytest.approx(24)
    # Heron: s = 12 → A = √(12·5·4·3) = √720
    assert float(detalhe(resultado, "Área (Heron)")) == pytest.approx(26.832816, abs=1e-5)


def test_triangulo_invalido(run_op):
    """1 + 1 ≤ 3 → as medidas não satisfazem a desigualdade triangular."""
    with pytest.raises(OpError, match="não formam um triângulo"):
        run_op("geo.triangulo_lados", a=1, b=1, c=3)


def test_triangulo_lado_nao_positivo(run_op):
    with pytest.raises(OpError, match="positivo"):
        run_op("geo.triangulo_lados", a=3, b=4, c=0)


def test_pitagoras_hipotenusa(run_op):
    resultado = run_op("geo.pitagoras", a=3, b=4, c=None)
    assert resultado["display"] == "c = √(a² + b²) = √(9 + 16) = 5"


def test_pitagoras_cateto(run_op):
    resultado = run_op("geo.pitagoras", a=None, b=4, c=5)
    assert resultado["details"][0]["value"] == "3"


def test_pitagoras_campos_errados(run_op):
    with pytest.raises(OpError, match="exatamente dois"):
        run_op("geo.pitagoras", a=3, b=None, c=None)
    with pytest.raises(OpError, match="exatamente dois"):
        run_op("geo.pitagoras", a=3, b=4, c=5)


def test_pitagoras_hipotenusa_menor_que_cateto(run_op):
    with pytest.raises(OpError, match="hipotenusa"):
        run_op("geo.pitagoras", a=5, b=None, c=3)


def test_circulo(run_op, detalhe):
    resultado = run_op("geo.circulo", raio=5)
    assert float(detalhe(resultado, "Diâmetro")) == pytest.approx(10)
    assert float(detalhe(resultado, "Área")) == pytest.approx(78.539816, abs=1e-5)
    assert float(detalhe(resultado, "Comprimento")) == pytest.approx(31.415927, abs=1e-5)


def test_circulo_raio_zero(run_op):
    with pytest.raises(OpError, match="positivo"):
        run_op("geo.circulo", raio=0)


def test_cubo(run_op, detalhe):
    resultado = run_op("geo.cubo", lado=3)
    assert float(detalhe(resultado, "Volume")) == pytest.approx(27)
    assert float(detalhe(resultado, "Área da superfície")) == pytest.approx(54)
    assert float(detalhe(resultado, "Diagonal do espaço")) == pytest.approx(5.196152, abs=1e-5)


def test_esfera(run_op, detalhe):
    import math

    resultado = run_op("geo.esfera", raio=6)
    assert float(detalhe(resultado, "Volume")) == pytest.approx(4 / 3 * math.pi * 216)
    assert float(detalhe(resultado, "Área")) == pytest.approx(4 * math.pi * 36)
