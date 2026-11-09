"""Testes das operações de criptografia de curvas elípticas (ECC).

Curva de exemplo: y² ≡ x³ + 7 (mod 79) — |E(Fp)| = 67 (primo), pelo que
P = (1, 18) é gerador de todo o grupo (todo o Q ≠ O está em ⟨P⟩).

Os valores esperados foram cruzados com uma implementação independente
(soma repetida, sem double-and-add).
"""

import pytest

from ops.helpers import OpError

P = (1, 18)          # gerador, ordem 67
Q = (6, 12)          # outro ponto da curva
MENOS_P = (1, 61)    # −P


def test_ponto_na_curva(run_op, detalhe):
    resultado = run_op("ecc.validar", a=0, b=7, p=79, x=1, y=18)
    assert resultado["display"] == "P = (1, 18) está na curva ✓"
    assert detalhe(resultado, "Pertence à curva") == "sim"
    assert detalhe(resultado, "N.º de pontos |E(Fp)|") == "67"


def test_ponto_fora_da_curva(run_op, detalhe):
    resultado = run_op("ecc.validar", a=0, b=7, p=79, x=1, y=19)
    assert "NÃO está na curva ✗" in resultado["display"]
    assert detalhe(resultado, "Pertence à curva") == "não"
    assert any("Não pertence" in step for step in resultado["steps"])


def test_validar_conta_respeita_os_limites_de_hasse(run_op):
    resultado = run_op("ecc.validar", a=0, b=7, p=79, x=6, y=12)
    assert any("Hasse" in step for step in resultado["steps"])


def test_soma_de_pontos_distintos(run_op):
    resultado = run_op("ecc.soma", a=0, b=7, p=79, x1=1, y1=18, x2=6, y2=12)
    assert resultado["display"] == "P + Q = (45, 19)"
    assert any("P ≠ Q" in step for step in resultado["steps"])


def test_soma_duplicacao(run_op):
    resultado = run_op("ecc.soma", a=0, b=7, p=79, x1=1, y1=18, x2=1, y2=18)
    assert resultado["display"] == "P + Q = (60, 10)"
    assert any("duplicação" in step for step in resultado["steps"])


def test_soma_com_o_oposto_da_curva(run_op):
    resultado = run_op("ecc.soma", a=0, b=7, p=79, x1=1, y1=18, x2=1, y2=61)
    assert resultado["display"] == "P + Q = O (ponto no infinito)"
    assert any("ponto no infinito" in step for step in resultado["steps"])


def test_multiplicacao_escalar_direto(run_op, detalhe):
    resultado = run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=18, k=13)
    assert resultado["display"] == "13 · P = (39, 47)"
    assert detalhe(resultado, "k (binário)") == "1101₂"
    assert any("double-and-add" in step for step in resultado["steps"])


def test_multiplicacao_casos_verificados(run_op):
    """Valores cruzados com soma repetida (referência independente)."""
    esperados = {1: (1, 18), 2: (60, 10), 20: (29, 8), 33: (27, 63), 66: (1, 61)}
    for k, ponto in esperados.items():
        resultado = run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=18, k=k)
        assert resultado["display"] == f"{k} · P = ({ponto[0]}, {ponto[1]})"


def test_multiplicacao_ordem_do_ponto(run_op):
    """A ordem de P é 67 → 67 · P = O (ponto no infinito)."""
    resultado = run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=18, k=67)
    assert resultado["display"] == "67 · P = O (ponto no infinito)"


def test_multiplicacao_k_zero(run_op):
    resultado = run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=18, k=0)
    assert "O (ponto no infinito)" in resultado["display"]


def test_inverso_recupera_k(run_op, detalhe):
    resultado = run_op("ecc.inverso", a=0, b=7, p=79, x1=1, y1=18, x2=29, y2=8)
    assert detalhe(resultado, "k (logaritmo discreto)") == "20"
    assert "k = 20" in resultado["display"]
    assert any("Verificação no sentido direto" in step for step in resultado["steps"])


@pytest.mark.parametrize("k", [1, 2, 13, 33, 66])
def test_inverso_parametrizado(run_op, k):
    """Q = k · P recupera sempre o menor k (0 ≤ k < 67)."""
    resultados = {
        1: (1, 18),
        2: (60, 10),
        13: (39, 47),
        33: (27, 63),
        66: (1, 61),
    }
    x2, y2 = resultados[k]
    resultado = run_op("ecc.inverso", a=0, b=7, p=79, x1=1, y1=18, x2=x2, y2=y2)
    assert resultado["details"][0]["value"] == str(k)


def test_erros_p_nao_primo(run_op):
    with pytest.raises(OpError, match="primo"):
        run_op("ecc.validar", a=0, b=7, p=100, x=1, y=1)


def test_erros_curva_singular(run_op):
    """a = 1, b = 1, p = 31 → 4a³ + 27b² = 31 ≡ 0 (mod 31)."""
    with pytest.raises(OpError, match="singular"):
        run_op("ecc.validar", a=1, b=1, p=31, x=1, y=1)


def test_erros_ponto_fora_na_soma(run_op):
    with pytest.raises(OpError, match="não está na curva"):
        run_op("ecc.soma", a=0, b=7, p=79, x1=1, y1=19, x2=6, y2=12)


def test_erros_ponto_fora_na_multiplicacao(run_op):
    with pytest.raises(OpError, match="não está na curva"):
        run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=19, k=13)


def test_erros_k_negativo(run_op):
    with pytest.raises(OpError, match="negativo"):
        run_op("ecc.multiplicacao", a=0, b=7, p=79, x=1, y=18, k=-5)


def test_erros_q_fora_do_subgrupo(run_op):
    """p = 103: P = (0, 25) tem ordem 3, mas |E| = 111 → há pontos fora de ⟨P⟩."""
    with pytest.raises(OpError, match="subgrupo"):
        run_op("ecc.inverso", a=0, b=7, p=103, x1=0, y1=25, x2=1, y2=27)


def test_erros_ponto_fora_no_inverso(run_op):
    with pytest.raises(OpError, match="não está na curva"):
        run_op("ecc.inverso", a=0, b=7, p=79, x1=1, y1=18, x2=6, y2=13)
