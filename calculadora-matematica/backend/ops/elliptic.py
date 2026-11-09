"""Criptografia de curvas elípticas (ECC).

Mostra os dois sentidos da operação central das ECC:

  • **direto**  →  k · P    (multiplicação escalar — barata, método double-and-add)
  • **inverso** →  dado Q = k · P, recuperar k  (logaritmo discreto — caro)

Curva na forma breve de Weierstrass:  y² ≡ x³ + a·x + b (mod p), com p primo.
É o desequilíbrio entre estes dois sentidos que sustenta a segurança da
criptografia real; aqui usamos curvas pequenas para ver o cálculo completo.
"""

import math

from ops.helpers import OpError, fmt
from ops.registry import op

# Limites didáticos (para o cálculo ficar sempre rápido e legível)
LIMITE_P = 10**9           # p máximo
LIMITE_K = 10**12          # escalar k máximo
LIMITE_CONTAGEM = 100_000  # p máximo para contar |E(Fp)| ponto a ponto
MAX_PASSOS = 36            # passos do algoritmo mostrados antes de resumir

_PRIMOS_TESTE = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


# ------------------------------------------------------------- validação


def _eh_primo(n):
    """Miller–Rabin determinístico (bases até 37 — certo para n < 2⁶⁴)."""
    if n < 2:
        return False
    for primo in _PRIMOS_TESTE:
        if n % primo == 0:
            return n == primo
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in _PRIMOS_TESTE:
        x = pow(base, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _validar_curva(a, b, p):
    """Valida p (primo, no limite) e o discriminante — devolve a, b módulo p."""
    if p < 3 or not _eh_primo(p):
        raise OpError(f"'p' tem de ser um número primo ≥ 3 (recebido: {fmt(p)}).")
    if p > LIMITE_P:
        raise OpError(f"'p' demasiado grande para a demonstração (máximo {LIMITE_P}).")
    a, b = a % p, b % p
    # Δ = −16(4a³ + 27b²); como p é ímpar, Δ ≡ 0 ⇔ 4a³ + 27b² ≡ 0
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise OpError(
            f"Curva singular: 4a³ + 27b² ≡ 0 (mod {p}) — não forma um grupo elíptico."
        )
    return a, b


def _lado_esquerdo(y, p):
    """y² módulo p."""
    return (y * y) % p


def _lado_direito(x, a, b, p):
    """x³ + a·x + b módulo p."""
    return (x * x * x + a * x + b) % p


def _checar_ponto(P, a, b, p, nome):
    """Levanta OpError se o ponto não satisfaz a equação da curva."""
    x, y = P
    esquerdo, direito = _lado_esquerdo(y, p), _lado_direito(x, a, b, p)
    if esquerdo != direito:
        raise OpError(
            f"O ponto {nome} = ({x}, {y}) não está na curva: "
            f"y² ≡ {esquerdo} mas x³ + ax + b ≡ {direito} (mod {p})."
        )


def _inverso_mod(x, p):
    """Inverso de x módulo p primo (pequeno teorema de Fermat)."""
    x %= p
    if x == 0:
        raise OpError("Não existe inverso módulo p (denominador múltiplo de p).")
    return pow(x, p - 2, p)


# ------------------------------------------------------- aritmética do grupo


def _mostrar(P):
    """Representação amigável de um ponto ('O' = ponto no infinito)."""
    if P is None:
        return "O"
    return f"({P[0]}, {P[1]})"


def _negar(P, p):
    """−P: mesmo x com y oposto (ou O)."""
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def _soma(P, Q, a, p):
    """Soma de pontos P + Q (leis do grupo). None representa o ponto no infinito."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None  # Q = −P → ponto no infinito
        # duplicação: λ = (3x² + a) ÷ (2y)
        lambda_ = ((3 * x1 * x1 + a) * _inverso_mod(2 * y1, p)) % p
    else:
        # λ = (y₂ − y₁) ÷ (x₂ − x₁)
        lambda_ = ((y2 - y1) * _inverso_mod(x2 - x1, p)) % p
    x3 = (lambda_ * lambda_ - x1 - x2) % p
    y3 = (lambda_ * (x1 - x3) - y1) % p
    return (x3, y3)


def _multiplicar(k, P, a, p, passos=None):
    """k · P por double-and-add (esquerda→direita sobre os bits de k).

    Se `passos` for fornecido, recebe uma linha por operação do algoritmo.
    """
    R = None
    binario = bin(k)[2:]
    for indice, bit in enumerate(binario):
        pos = len(binario) - indice - 1
        R = _soma(R, R, a, p)  # dobrar
        if passos is not None:
            passos.append(f"bit {pos} ({fmt(2 ** pos)}): dobrar → {_mostrar(R)}")
        if bit == "1":
            R = _soma(R, P, a, p)  # adicionar
            if passos is not None:
                passos.append(f"bit {pos}: adicionar P → {_mostrar(R)}")
    return R


def _resumir(passos, limite=MAX_PASSOS):
    """Encurta listas de passos demasiado longas (mantém início e fim)."""
    if len(passos) <= limite:
        return passos
    meio = limite // 2
    inicio, fim = passos[:meio], passos[-meio:]
    omitidos = len(passos) - len(inicio) - len(fim)
    return inicio + [f"… ({omitidos} passos omitidos) …"] + fim


def _contar_pontos(a, b, p):
    """|E(Fp)| = 1 + Σₓ (1 + legendre(x³ + ax + b, p)) — O(p)."""
    total = 1  # ponto no infinito
    for x in range(p):
        rhs = _lado_direito(x, a, b, p)
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:  # é resíduo quadrático → 2 valores de y
            total += 2
    return total


def _limite_hasse(p):
    """Maior inteiro garantido ≥ |E(Fp)| (limites de Hasse, arredondados por cima)."""
    return math.ceil(p + 1 + 2 * math.sqrt(p)) + 1


# ---------------------------------------------------------- operações


@op(
    "ecc.validar",
    "criptografia",
    "Ponto numa curva elíptica",
    "Verifica se P = (x, y) satisfaz y² ≡ x³ + a·x + b (mod p) e conta os pontos da curva.",
    [
        {"name": "a", "label": "a (coeficiente de x)", "type": "integer", "placeholder": "ex: 2"},
        {"name": "b", "label": "b (termo independente)", "type": "integer", "placeholder": "ex: 7"},
        {"name": "p", "label": "p (primo, módulo)", "type": "integer", "placeholder": "ex: 97"},
        {"name": "x", "label": "x do ponto P", "type": "integer", "placeholder": "ex: 3"},
        {"name": "y", "label": "y do ponto P", "type": "integer", "placeholder": "ex: 10"},
    ],
    order=1,
)
def ponto_na_curva(a, b, p, x, y):
    a, b = _validar_curva(a, b, p)
    x, y = x % p, y % p
    esquerdo = _lado_esquerdo(y, p)
    direito = _lado_direito(x, a, b, p)
    pertence = esquerdo == direito

    steps = [
        f"Curva: y² ≡ x³ + {fmt(a)}x + {fmt(b)} (mod {fmt(p)})",
        f"Lado esquerdo: y² = {fmt(y)}² = {fmt(esquerdo)} (mod {fmt(p)})",
        f"Lado direito: x³ + ax + b = {fmt(x)}³ + {fmt(a)}·{fmt(x)} + {fmt(b)} = {fmt(direito)} (mod {fmt(p)})",
        f"{'Pertence à curva ✓' if pertence else f'Não pertence ✗ — {fmt(esquerdo)} ≠ {fmt(direito)} (mod {fmt(p)})'}",
    ]
    details = [
        {"label": "y² mod p", "value": fmt(esquerdo)},
        {"label": "x³ + ax + b mod p", "value": fmt(direito)},
        {"label": "Pertence à curva", "value": "sim" if pertence else "não"},
    ]

    if p <= LIMITE_CONTAGEM:
        total = _contar_pontos(a, b, p)
        inferior = math.floor(p + 1 - 2 * math.sqrt(p))
        superior = math.ceil(p + 1 + 2 * math.sqrt(p))
        steps += [
            f"Contagem ponto a ponto: |E(Fp)| = {fmt(total)} pontos (inclui O)",
            f"Limites de Hasse: {fmt(inferior)} ≤ |E(Fp)| ≤ {fmt(superior)} ✓",
        ]
        details.append({"label": "N.º de pontos |E(Fp)|", "value": fmt(total)})
    else:
        steps.append(
            f"p > {fmt(LIMITE_CONTAGEM)} → contagem de pontos omitida (seria lenta)."
        )

    display = (
        f"P = ({fmt(x)}, {fmt(y)}) está na curva ✓"
        if pertence
        else f"P = ({fmt(x)}, {fmt(y)}) NÃO está na curva ✗"
    )
    return {"display": display, "steps": steps, "details": details}


@op(
    "ecc.soma",
    "criptografia",
    "Soma de pontos (P + Q)",
    "Soma dois pontos na curva y² ≡ x³ + a·x + b (mod p) — a operação do grupo elíptico.",
    [
        {"name": "a", "label": "a (coeficiente de x)", "type": "integer", "placeholder": "ex: 2"},
        {"name": "b", "label": "b (termo independente)", "type": "integer", "placeholder": "ex: 7"},
        {"name": "p", "label": "p (primo, módulo)", "type": "integer", "placeholder": "ex: 97"},
        {"name": "x1", "label": "x do ponto P", "type": "integer", "placeholder": "ex: 3"},
        {"name": "y1", "label": "y do ponto P", "type": "integer", "placeholder": "ex: 10"},
        {"name": "x2", "label": "x do ponto Q", "type": "integer", "placeholder": "ex: 10"},
        {"name": "y2", "label": "y do ponto Q", "type": "integer", "placeholder": "ex: 7"},
    ],
    order=2,
)
def soma_de_pontos(a, b, p, x1, y1, x2, y2):
    a, b = _validar_curva(a, b, p)
    x1, y1, x2, y2 = x1 % p, y1 % p, x2 % p, y2 % p
    P, Q = (x1, y1), (x2, y2)
    _checar_ponto(P, a, b, p, "P")
    _checar_ponto(Q, a, b, p, "Q")

    steps = [
        f"P = {_mostrar(P)} e Q = {_mostrar(Q)} pertencem à curva ✓ (mod {fmt(p)})",
    ]

    R = _soma(P, Q, a, p)

    if R is None:
        if P == Q:
            steps.append("y = 0 → a tangente é vertical → P + P = O (ponto no infinito)")
        else:
            steps.append("Q = −P (mesmo x, y opostos) → P + Q = O (ponto no infinito)")
    elif P == Q:
        denominador = (2 * y1) % p
        lambda_ = ((3 * x1 * x1 + a) * _inverso_mod(denominador, p)) % p
        steps += [
            f"P = Q → duplicação: λ = (3x² + a) ÷ (2y) = {fmt((3 * x1 * x1 + a) % p)} ÷ "
            f"{fmt(denominador)} = {fmt(lambda_)} (mod {fmt(p)})",
            f"x₃ = λ² − x₁ − x₂ = {fmt(lambda_)}² − {fmt(x1)} − {fmt(x1)} = {fmt(R[0])} (mod {fmt(p)})",
            f"y₃ = λ(x₁ − x₃) − y₁ = {fmt(lambda_)}·({fmt(x1)} − {fmt(R[0])}) − {fmt(y1)} = {fmt(R[1])} (mod {fmt(p)})",
        ]
    else:
        lambda_ = ((y2 - y1) * _inverso_mod(x2 - x1, p)) % p
        steps += [
            f"P ≠ Q → λ = (y₂ − y₁) ÷ (x₂ − x₁) = {fmt((y2 - y1) % p)} ÷ "
            f"{fmt((x2 - x1) % p)} = {fmt(lambda_)} (mod {fmt(p)})",
            f"x₃ = λ² − x₁ − x₂ = {fmt(lambda_)}² − {fmt(x1)} − {fmt(x2)} = {fmt(R[0])} (mod {fmt(p)})",
            f"y₃ = λ(x₁ − x₃) − y₁ = {fmt(lambda_)}·({fmt(x1)} − {fmt(R[0])}) − {fmt(y1)} = {fmt(R[1])} (mod {fmt(p)})",
        ]
        if R == P or R == Q:
            steps.append("A soma deu um dos pontos originais — verifique os valores.")

    display = (
        f"P + Q = {_mostrar(R)} (ponto no infinito)"
        if R is None
        else f"P + Q = {_mostrar(R)}"
    )
    details = [
        {"label": "P", "value": _mostrar(P)},
        {"label": "Q", "value": _mostrar(Q)},
        {"label": "P + Q", "value": _mostrar(R) + (" (ponto no infinito)" if R is None else "")},
    ]
    return {"display": display, "steps": steps, "details": details}


@op(
    "ecc.multiplicacao",
    "criptografia",
    "Multiplicação escalar (direto)",
    "Calcula k · P pelo método double-and-add — o sentido DIRETO, rápido e usado nas chaves.",
    [
        {"name": "a", "label": "a (coeficiente de x)", "type": "integer", "placeholder": "ex: 2"},
        {"name": "b", "label": "b (termo independente)", "type": "integer", "placeholder": "ex: 7"},
        {"name": "p", "label": "p (primo, módulo)", "type": "integer", "placeholder": "ex: 97"},
        {"name": "x", "label": "x do ponto P", "type": "integer", "placeholder": "ex: 3"},
        {"name": "y", "label": "y do ponto P", "type": "integer", "placeholder": "ex: 10"},
        {"name": "k", "label": "k (escalar)", "type": "integer", "placeholder": "ex: 13"},
    ],
    order=3,
)
def multiplicacao_escalar(a, b, p, x, y, k):
    a, b = _validar_curva(a, b, p)
    x, y = x % p, y % p
    if k < 0:
        raise OpError("O escalar k não pode ser negativo.")
    if k > LIMITE_K:
        raise OpError(f"k demasiado grande para a demonstração (máximo {LIMITE_K}).")
    P = (x, y)
    _checar_ponto(P, a, b, p, "P")

    binario = bin(k)[2:]
    passos = [
        f"P = {_mostrar(P)} pertence à curva ✓ (mod {fmt(p)})",
        f"k = {fmt(k)} = {binario}₂  ({len(binario)} bits, {binario.count('1')} uns)",
        "Método double-and-add: percorrer os bits de k da esquerda para a direita, "
        "dobrando R a cada bit e somando P quando o bit é 1.",
    ]
    R = _multiplicar(k, P, a, p, passos)
    passos = _resumir(passos)
    passos.append(f"Resultado: k · P = {_mostrar(R)}")

    resultado = "O (ponto no infinito)" if R is None else _mostrar(R)
    return {
        "display": f"{fmt(k)} · P = {resultado}",
        "steps": passos,
        "details": [
            {"label": "k (decimal)", "value": fmt(k)},
            {"label": "k (binário)", "value": f"{binario}₂"},
            {"label": "k · P", "value": resultado},
        ],
    }


@op(
    "ecc.inverso",
    "criptografia",
    "Logaritmo discreto (inverso)",
    "Dado Q = k · P, encontra k — o sentido INVERSO (baby-step giant-step), o problema difícil.",
    [
        {"name": "a", "label": "a (coeficiente de x)", "type": "integer", "placeholder": "ex: 2"},
        {"name": "b", "label": "b (termo independente)", "type": "integer", "placeholder": "ex: 7"},
        {"name": "p", "label": "p (primo, módulo)", "type": "integer", "placeholder": "ex: 97"},
        {"name": "x1", "label": "x do ponto P", "type": "integer", "placeholder": "ex: 3"},
        {"name": "y1", "label": "y do ponto P", "type": "integer", "placeholder": "ex: 10"},
        {"name": "x2", "label": "x do ponto Q", "type": "integer", "placeholder": "ex: 15"},
        {"name": "y2", "label": "y do ponto Q", "type": "integer", "placeholder": "ex: 60"},
    ],
    order=4,
)
def logaritmo_discreto(a, b, p, x1, y1, x2, y2):
    a, b = _validar_curva(a, b, p)
    x1, y1, x2, y2 = x1 % p, y1 % p, x2 % p, y2 % p
    P, Q = (x1, y1), (x2, y2)
    _checar_ponto(P, a, b, p, "P")
    _checar_ponto(Q, a, b, p, "Q")

    limite = _limite_hasse(p)
    m = math.isqrt(limite) + 1  # m² > limite → todos os k candidatos cabem

    # passos de bebé: tabela {j · P : 0 ≤ j < m}
    tabela = {}
    ponto = None
    for j in range(m):
        tabela.setdefault(ponto, j)
        ponto = _soma(ponto, P, a, p)

    # passos de gigante: comparar Q − i · (m · P) com a tabela
    passo = _multiplicar(m, P, a, p)
    menos_passo = _negar(passo, p)
    gamma = Q
    encontrado = None
    for i in range(m + 1):
        j = tabela.get(gamma)
        if j is not None:
            encontrado = (i, j)
            break
        gamma = _soma(gamma, menos_passo, a, p)

    if encontrado is None:
        raise OpError(
            "Não existe k tal que k · P = Q: o ponto Q não está no subgrupo "
            f"gerado por P (k teria de ser ≥ {fmt(m * m)})."
        )

    i, j = encontrado
    k = i * m + j

    verificacao = _multiplicar(k, P, a, p)
    assert verificacao == Q  # invariante interno (não deve acontecer)

    steps = [
        f"Sentido inverso: encontrar k com k · P = Q = {_mostrar(Q)} "
        "(é o problema do logaritmo discreto — o difícil das ECC).",
        f"Limite de Hasse: k < |E(Fp)| ≤ {fmt(limite)}",
        f"Passos de bebé: tabela de j · P para j = 0 … {fmt(m - 1)}  ({fmt(m)} pontos)",
        f"Passos de gigante: comparar Q − i · ({fmt(m)} · P) na tabela, i = 0 … {fmt(m)}",
        f"Encontrado: k = {fmt(i)} × {fmt(m)} + {fmt(j)} = {fmt(k)}",
        f"Verificação no sentido direto: {fmt(k)} · P = Q ✓",
    ]

    return {
        "display": f"k = {fmt(k)}   (k · P = Q)",
        "steps": steps,
        "details": [
            {"label": "k (logaritmo discreto)", "value": fmt(k)},
            {"label": "P", "value": _mostrar(P)},
            {"label": "Q = k · P", "value": _mostrar(Q)},
            {"label": "Passos de bebé/gigante (m)", "value": fmt(m)},
        ],
    }
