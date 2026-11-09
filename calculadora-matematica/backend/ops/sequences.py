"""Progressões aritméticas (PA) e geométricas (PG)."""

from ops.helpers import OpError, fmt
from ops.registry import op


def _validar(n):
    if n < 1:
        raise OpError("O número de termos tem de ser pelo menos 1.")


def _preview(termos, n):
    """Lista os termos quando a sequência é curta o suficiente para mostrar."""
    if n > 8:
        return None
    return "Termos: " + ", ".join(fmt(t) for t in termos)

@op(
    "prog.pa",
    "progressoes",
    "Progressão aritmética (PA)",
    "Dado o 1.º termo (a₁) e a razão (r), calcula o n-ésimo termo e a soma dos n primeiros.",
    [
        {"name": "a1", "label": "1.º termo (a₁)", "type": "number", "placeholder": "ex: 3"},
        {"name": "razao", "label": "Razão (r)", "type": "number", "placeholder": "ex: 5"},
        {"name": "n", "label": "N.º de termos (n)", "type": "integer", "placeholder": "ex: 20"},
    ],
    order=1,
)
def progressao_aritmetica(a1, razao, n):
    _validar(n)
    ultimo = a1 + (n - 1) * razao
    soma = n * (a1 + ultimo) / 2

    steps = [
        "Termo geral: aₙ = a₁ + (n − 1)·r",
        f"a{n} = {fmt(a1)} + ({n} − 1)×{fmt(razao)} = {fmt(a1)} + {fmt((n - 1) * razao)} = {fmt(ultimo)}",
        f"Soma: Sₙ = n × (a₁ + aₙ) ÷ 2 = {n} × ({fmt(a1)} + {fmt(ultimo)}) ÷ 2 = {fmt(soma)}",
    ]
    if n <= 8:
        termos = [a1 + i * razao for i in range(n)]
        steps.append(_preview(termos, n))

    return {
        "display": f"aₙ = {fmt(ultimo)}  |  Sₙ = {fmt(soma)}",
        "steps": steps,
        "details": [
            {"label": f"a{n} (n-ésimo termo)", "value": fmt(ultimo)},
            {"label": f"S{n} (soma)", "value": fmt(soma)},
        ],
    }


@op(
    "prog.pg",
    "progressoes",
    "Progressão geométrica (PG)",
    "Dado o 1.º termo (a₁) e a razão (q), calcula o n-ésimo termo e a soma dos n primeiros.",
    [
        {"name": "a1", "label": "1.º termo (a₁)", "type": "number", "placeholder": "ex: 2"},
        {"name": "razao", "label": "Razão (q)", "type": "number", "placeholder": "ex: 3"},
        {"name": "n", "label": "N.º de termos (n)", "type": "integer", "placeholder": "ex: 5"},
    ],
    order=2,
)
def progressao_geometrica(a1, razao, n):
    _validar(n)
    try:
        ultimo = a1 * razao ** (n - 1)
        if razao == 1:
            soma = n * a1
            passo_soma = f"q = 1 → Sₙ = n × a₁ = {n} × {fmt(a1)} = {fmt(soma)}"
        else:
            soma = a1 * (1 - razao**n) / (1 - razao)
            passo_soma = (
                f"Sₙ = a₁ × (1 − qⁿ) ÷ (1 − q) = {fmt(a1)} × (1 − {fmt(razao ** n)}) "
                f"÷ (1 − {fmt(razao)}) = {fmt(soma)}"
            )
    except OverflowError:
        raise OpError("Resultado demasiado grande para esta razão e este número de termos.")

    steps = [
        "Termo geral: aₙ = a₁ · q^(n−1)",
        f"a{n} = {fmt(a1)} × {fmt(razao)}^({n} − 1) = {fmt(ultimo)}",
        passo_soma,
    ]
    if n <= 8:
        termos = [a1 * razao**i for i in range(n)]
        steps.append(_preview(termos, n))

    return {
        "display": f"aₙ = {fmt(ultimo)}  |  Sₙ = {fmt(soma)}",
        "steps": steps,
        "details": [
            {"label": f"a{n} (n-ésimo termo)", "value": fmt(ultimo)},
            {"label": f"S{n} (soma)", "value": fmt(soma)},
        ],
    }
