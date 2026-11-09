"""Testes das operações novas: logaritmos, progressões, trigonometria,
matrizes, probabilidade e unidades (16 operações)."""

import pytest

from ops.helpers import OpError


# ------------------------------------------------------------- logaritmos


def test_logaritmo_base_livre(run_op):
    assert run_op("log.base", base=2, value=32)["display"] == "log base 2 de 32 = 5"
    assert run_op("log.base", base=10, value=1000)["display"] == "log base 10 de 1000 = 3"


def test_logaritmo_base_invalida(run_op):
    with pytest.raises(OpError, match="base"):
        run_op("log.base", base=1, value=10)
    with pytest.raises(OpError, match="positivo"):
        run_op("log.base", base=-2, value=10)


def test_logaritmo_argumento_invalido(run_op):
    with pytest.raises(OpError, match="positivo"):
        run_op("log.base", base=2, value=-5)
    with pytest.raises(OpError):
        run_op("log.base", base=2, value=0)


def test_equacao_logaritmica(run_op, detalhe):
    resultado = run_op("log.inverso", base=10, logaritmo=2.5)
    assert float(detalhe(resultado, "x")) == pytest.approx(10**2.5, rel=1e-6)


# ------------------------------------------------------------- progressões


def test_progressao_aritmetica(run_op, detalhe):
    # a₁ = 3, r = 5, n = 20 → aₙ = 3 + 19·5 = 98, Sₙ = 20·(3 + 98)/2 = 1010
    resultado = run_op("prog.pa", a1=3, razao=5, n=20)
    assert resultado["display"] == "aₙ = 98  |  Sₙ = 1010"
    assert float(detalhe(resultado, "a20 (n-ésimo termo)")) == pytest.approx(98)
    assert float(detalhe(resultado, "S20 (soma)")) == pytest.approx(1010)


def test_progressao_aritmetica_n_invalido(run_op):
    with pytest.raises(OpError, match="pelo menos 1"):
        run_op("prog.pa", a1=1, razao=1, n=0)


def test_progressao_geometrica(run_op, detalhe):
    # a₁ = 2, q = 3, n = 5 → aₙ = 2·3⁴ = 162, Sₙ = 2·(1 − 243)/(1 − 3) = 242
    resultado = run_op("prog.pg", a1=2, razao=3, n=5)
    assert resultado["display"] == "aₙ = 162  |  Sₙ = 242"
    assert float(detalhe(resultado, "S5 (soma)")) == pytest.approx(242)


def test_progressao_geometrica_razao_un(run_op, detalhe):
    """q = 1 → fórmula especial Sₙ = n · a₁ (senão daria 0/0)."""
    resultado = run_op("prog.pg", a1=4, razao=1, n=5)
    assert float(detalhe(resultado, "a5 (n-ésimo termo)")) == pytest.approx(4)
    assert float(detalhe(resultado, "S5 (soma)")) == pytest.approx(20)


# ----------------------------------------------------------- trigonometria


def test_funcao_trigonometrica_graus(run_op):
    assert run_op("trig.funcao", funcao="sen", angulo=30, unidade="graus")["display"] == "sen(30°) = 0.5"
    # cos(90°) ≈ 6.1e-17 → tem de ser suavizado para 0
    assert run_op("trig.funcao", funcao="cos", angulo=90, unidade="graus")["display"] == "cos(90°) = 0"


def test_funcao_trigonometrica_radianos(run_op, detalhe):
    import math

    resultado = run_op("trig.funcao", funcao="cos", angulo=math.pi, unidade="radianos")
    assert float(detalhe(resultado, "cos(3.141593)")) == pytest.approx(-1, abs=1e-9)


def test_tangente_de_90_graus(run_op):
    """tan(90°) não existe (cosseno = 0)."""
    with pytest.raises(OpError, match="tangente"):
        run_op("trig.funcao", funcao="tan", angulo=90, unidade="graus")


def test_funcao_invalida(run_op):
    # a validação acontece já na coerção do campo select
    with pytest.raises(OpError, match="Opção inválida"):
        run_op("trig.funcao", funcao="cot", angulo=30, unidade="graus")


def test_triangulo_retangulo(run_op, detalhe):
    # c = 10, A = 30° → oposto = 5, adjacente = 5√3 ≈ 8.660254
    resultado = run_op("trig.retangulo", hipotenusa=10, angulo=30)
    assert float(detalhe(resultado, "Cateto oposto")) == pytest.approx(5)
    assert float(detalhe(resultado, "Cateto adjacente")) == pytest.approx(8.660254, abs=1e-5)


def test_triangulo_retangulo_angulo_invalido(run_op):
    with pytest.raises(OpError, match="0° e 90°"):
        run_op("trig.retangulo", hipotenusa=10, angulo=100)


def test_triangulo_retangulo_hipotenusa_invalida(run_op):
    with pytest.raises(OpError, match="positivo"):
        run_op("trig.retangulo", hipotenusa=0, angulo=30)


def test_lei_dos_senos(run_op, detalhe):
    # a = 8, A = 60°, B = 45° → C = 75°, b = 8·sen45/sen60, c = 8·sen75/sen60
    resultado = run_op("trig.lei_senos", a=8, angulo_A=60, angulo_B=45)
    assert detalhe(resultado, "Ângulo C") == "75°"
    assert float(detalhe(resultado, "Lado b")) == pytest.approx(6.531973, abs=1e-5)
    assert float(detalhe(resultado, "Lado c")) == pytest.approx(8.922841, abs=1e-5)


def test_lei_dos_senos_soma_de_angulos(run_op):
    with pytest.raises(OpError, match="inferior a 180°"):
        run_op("trig.lei_senos", a=5, angulo_A=120, angulo_B=80)


def test_lei_dos_senos_angulo_invalido(run_op):
    with pytest.raises(OpError, match="entre 0° e 180°"):
        run_op("trig.lei_senos", a=5, angulo_A=0, angulo_B=45)


# ------------------------------------------------------------------ matrizes


def test_determinante_2x2(run_op, detalhe):
    resultado = run_op("mat.determinante", linha1=[1, 2], linha2=[3, 4], linha3=None)
    assert resultado["display"] == "det(A) = -2"
    assert detalhe(resultado, "Determinante") == "-2"


def test_determinante_3x3_singular(run_op):
    # Linhas dependentes → det = 0
    resultado = run_op(
        "mat.determinante", linha1=[2, 0, 1], linha2=[1, 3, 2], linha3=[1, 1, 1]
    )
    assert resultado["display"] == "det(A) = 0"
    assert any("singular" in step for step in resultado["steps"])


def test_determinante_nao_quadrada(run_op):
    with pytest.raises(OpError, match="quadradas"):
        run_op("mat.determinante", linha1=[1, 2, 3], linha2=[4, 5, 6], linha3=None)


def test_determinante_linhas_de_tamanhos_diferentes(run_op):
    with pytest.raises(OpError, match="retangular"):
        run_op("mat.determinante", linha1=[1, 2], linha2=[3, 4, 5], linha3=None)


def test_soma_de_matrizes(run_op):
    resultado = run_op(
        "mat.soma",
        a1=[1, 2], a2=[3, 4], a3=None,
        b1=[10, 20], b2=[30, 40], b3=None,
    )
    assert resultado["display"] == "[11 22 ; 33 44]"


def test_soma_de_matrizes_tamanhos_diferentes(run_op):
    with pytest.raises(OpError, match="mesmo tamanho"):
        run_op(
            "mat.soma",
            a1=[1, 2], a2=[3, 4], a3=None,
            b1=[1, 2, 3], b2=[4, 5, 6], b3=None,
        )


def test_multiplicacao_de_matrizes(run_op):
    # [1 2; 3 4] × [10 20; 30 40] = [70 100; 150 220]
    resultado = run_op(
        "mat.multiplicacao",
        a1=[1, 2], a2=[3, 4], a3=None,
        b1=[10, 20], b2=[30, 40], b3=None,
    )
    assert resultado["display"] == "[70 100 ; 150 220]"


def test_multiplicacao_de_matrizes_impossivel(run_op):
    """A (2×3) · B (2×2): colunas de A ≠ linhas de B."""
    with pytest.raises(OpError, match="coluna"):
        run_op(
            "mat.multiplicacao",
            a1=[1, 2, 3], a2=[4, 5, 6], a3=None,
            b1=[1, 2], b2=[3, 4], b3=None,
        )


# -------------------------------------------------------------- probabilidade


def test_probabilidade_de_evento(run_op, detalhe):
    resultado = run_op("prob.evento", favoraveis=3, possiveis=8)
    assert resultado["display"] == "P(A) = 0.375  (37.5%)"
    assert float(detalhe(resultado, "P(não A)")) == pytest.approx(0.625)


def test_probabilidade_favoraveis_a_mais(run_op):
    with pytest.raises(OpError, match="superar"):
        run_op("prob.evento", favoraveis=9, possiveis=8)


def test_probabilidade_sem_possiveis(run_op):
    with pytest.raises(OpError, match="maiores que zero"):
        run_op("prob.evento", favoraveis=0, possiveis=0)


def test_permutacoes_e_combinacoes(run_op, detalhe):
    resultado = run_op("prob.combinacoes", n=5, k=3)
    assert resultado["display"] == "P(5, 3) = 60  |  C(5, 3) = 10"
    assert detalhe(resultado, "P(5, 3) — com ordem") == "60"
    assert detalhe(resultado, "C(5, 3) — sem ordem") == "10"


def test_combinacoes_k_maior_que_n(run_op):
    with pytest.raises(OpError, match="maior que n"):
        run_op("prob.combinacoes", n=3, k=5)


def test_combinacoes_n_grande(run_op):
    with pytest.raises(OpError, match="máximo"):
        run_op("prob.combinacoes", n=101, k=3)


def test_eventos_independentes(run_op, detalhe):
    resultado = run_op("prob.independentes", pa=0.6, pb=0.5)
    assert resultado["display"] == "P(A ∩ B) = 0.3  |  P(A ∪ B) = 0.8"
    assert float(detalhe(resultado, "P(A) · P(B)")) == pytest.approx(0.3)


def test_eventos_probabilidade_invalida(run_op):
    with pytest.raises(OpError, match="entre 0 e 1"):
        run_op("prob.independentes", pa=1.5, pb=0.5)
    with pytest.raises(OpError, match="entre 0 e 1"):
        run_op("prob.independentes", pa=0.5, pb=-0.1)


# ------------------------------------------------------------------- unidades


def test_conversao_de_comprimento(run_op, detalhe):
    resultado = run_op("un.comprimento", value=2.5, de="km", para="m")
    assert resultado["display"] == "2.5 km = 2500 m"
    assert float(detalhe(resultado, "Valor convertido").split()[0]) == pytest.approx(2500)


def test_conversao_de_comprimento_mesma_unidade(run_op):
    resultado = run_op("un.comprimento", value=5, de="m", para="m")
    assert resultado["display"] == "5 m = 5 m"
    assert any("mesma unidade" in step for step in resultado["steps"])


def test_conversao_de_massa(run_op):
    resultado = run_op("un.massa", value=750, de="g", para="kg")
    assert resultado["display"] == "750 g = 0.75 kg"


def test_conversao_de_massa_unidade_invalida(run_op):
    # 'lb' é válida; uma unidade inexistente é bloqueada na coerção do select
    with pytest.raises(OpError, match="Opção inválida"):
        run_op("un.massa", value=1, de="stone", para="kg")


def test_conversao_de_temperatura_celsius_fahrenheit(run_op):
    resultado = run_op("un.temperatura", value=25, de="C", para="F")
    assert resultado["display"] == "25 C = 77 F"


def test_conversao_de_temperatura_kelvin(run_op):
    resultado = run_op("un.temperatura", value=0, de="K", para="C")
    assert resultado["display"] == "0 K = -273.15 C"


def test_temperatura_kelvin_negativo(run_op):
    """K < 0 é fisicamente impossível — bloqueado antes da conversão."""
    with pytest.raises(OpError, match="Kelvin"):
        run_op("un.temperatura", value=-10, de="K", para="C")


def test_temperatura_abaixo_do_zero_absoluto(run_op):
    with pytest.raises(OpError, match="zero absoluto"):
        run_op("un.temperatura", value=-300, de="C", para="K")
