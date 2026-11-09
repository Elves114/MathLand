"""Operações de probabilidade básica."""

import math

from ops.helpers import OpError, fmt
from ops.registry import op

LIMITE_N = 100  # acima disto, o fatorial fica ilegível nos passos


@op(
    "prob.evento",
    "probabilidade",
    "Probabilidade de um evento",
    "P = casos favoráveis ÷ casos possíveis (mostra também a percentagem e o evento complementar).",
    [
        {"name": "favoraveis", "label": "Casos favoráveis", "type": "integer", "placeholder": "ex: 3"},
        {"name": "possiveis", "label": "Casos possíveis", "type": "integer", "placeholder": "ex: 8"},
    ],
    order=1,
)
def probabilidade_evento(favoraveis, possiveis):
    if possiveis <= 0:
        raise OpError("Os casos possíveis têm de ser maiores que zero.")
    if favoraveis < 0:
        raise OpError("Os casos favoráveis não podem ser negativos.")
    if favoraveis > possiveis:
        raise OpError("Os casos favoráveis não podem superar os casos possíveis.")

    prob = favoraveis / possiveis
    complementar = 1 - prob

    steps = [
        f"P(A) = favoráveis ÷ possíveis = {favoraveis} ÷ {possiveis} = {fmt(prob)}",
        f"Em percentagem: {fmt(prob)} × 100 = {fmt(prob * 100)}%",
        f"Evento complementar: P(não A) = 1 − {fmt(prob)} = {fmt(complementar)} "
        f"({fmt(complementar * 100)}%)",
    ]
    if prob in (0.0, 1.0):
        steps.append("P = 0 → evento impossível." if prob == 0 else "P = 1 → evento certo.")

    return {
        "display": f"P(A) = {fmt(prob)}  ({fmt(prob * 100)}%)",
        "steps": steps,
        "details": [
            {"label": "Probabilidade P(A)", "value": fmt(prob)},
            {"label": "Percentagem", "value": f"{fmt(prob * 100)}%"},
            {"label": "P(não A)", "value": fmt(complementar)},
        ],
    }


@op(
    "prob.combinacoes",
    "probabilidade",
    "Permutações e combinações",
    "P(n, k) = n! ÷ (n−k)!  e  C(n, k) = n! ÷ (k! · (n−k)!).",
    [
        {"name": "n", "label": "Total de elementos (n)", "type": "integer", "placeholder": "ex: 5"},
        {"name": "k", "label": "Elementos a escolher (k)", "type": "integer", "placeholder": "ex: 3"},
    ],
    order=2,
)
def permutacoes_combinacoes(n, k):
    if n < 0 or k < 0:
        raise OpError("n e k não podem ser negativos.")
    if k > n:
        raise OpError("k não pode ser maior que n (não dá para escolher mais do que existe).")
    if n > LIMITE_N:
        raise OpError(f"n demasiado grande para mostrar o cálculo (máximo {LIMITE_N}).")

    fatorial_n = math.factorial(n)
    permutacoes = fatorial_n // math.factorial(n - k)
    combinacoes = fatorial_n // (math.factorial(k) * math.factorial(n - k))

    return {
        "display": f"P({n}, {k}) = {permutacoes}  |  C({n}, {k}) = {combinacoes}",
        "steps": [
            f"{n}! = {fatorial_n}",
            f"Com ordem: P({n}, {k}) = {n}! ÷ ({n} − {k})! = {fatorial_n} ÷ "
            f"{math.factorial(n - k)} = {permutacoes}",
            f"Sem ordem: C({n}, {k}) = {n}! ÷ ({k}! × ({n} − {k})!) = {fatorial_n} ÷ "
            f"({math.factorial(k)} × {math.factorial(n - k)}) = {combinacoes}",
            f"C({n}, {k}) é sempre ≤ P({n}, {k}) — a ordem não conta.",
        ],
        "details": [
            {"label": f"P({n}, {k}) — com ordem", "value": str(permutacoes)},
            {"label": f"C({n}, {k}) — sem ordem", "value": str(combinacoes)},
            {"label": f"{n}!", "value": str(fatorial_n)},
        ],
    }


@op(
    "prob.independentes",
    "probabilidade",
    "Eventos independentes",
    "P(A ∩ B) = P(A)·P(B) e P(A ∪ B) = P(A) + P(B) − P(A)·P(B).",
    [
        {"name": "pa", "label": "P(A)", "type": "number", "placeholder": "ex: 0.6",
         "hint": "Entre 0 e 1 (0.6 = 60%)."},
        {"name": "pb", "label": "P(B)", "type": "number", "placeholder": "ex: 0.5",
         "hint": "Entre 0 e 1 (0.5 = 50%)."},
    ],
    order=3,
)
def eventos_independentes(pa, pb):
    for nome, valor in (("P(A)", pa), ("P(B)", pb)):
        if not 0 <= valor <= 1:
            raise OpError(f"{nome} tem de estar entre 0 e 1 (ex.: 0.6 para 60%).")

    interseccao = pa * pb
    uniao = pa + pb - interseccao

    steps = [
        f"São independentes → P(A ∩ B) = P(A) × P(B) = {fmt(pa)} × {fmt(pb)} = {fmt(interseccao)}",
        f"União: P(A ∪ B) = P(A) + P(B) − P(A ∩ B) = {fmt(pa)} + {fmt(pb)} − "
        f"{fmt(interseccao)} = {fmt(uniao)}",
    ]
    if interseccao + uniao <= 1 + 1e-12:
        steps.append(
            f"Consistência: P(A ∩ B) + P(A ∪ B) = {fmt(interseccao + uniao)} ≤ 1 ✓"
        )

    return {
        "display": f"P(A ∩ B) = {fmt(interseccao)}  |  P(A ∪ B) = {fmt(uniao)}",
        "steps": steps,
        "details": [
            {"label": "P(A) · P(B)", "value": fmt(interseccao)},
            {"label": "P(A ∪ B)", "value": fmt(uniao)},
            {"label": "P(só A) = P(A)(1−P(B))", "value": fmt(pa * (1 - pb))},
            {"label": "P(só B) = P(B)(1−P(A))", "value": fmt(pb * (1 - pa))},
        ],
    }
