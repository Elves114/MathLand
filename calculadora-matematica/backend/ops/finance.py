"""Operações de finanças: juros simples e compostos."""

from ops.helpers import OpError, ensure_non_negative, fmt
from ops.registry import op

# Limites didáticos da taxa (em % por período)
TAXA_MINIMA = -100.0  # abaixo disso o montante ficaria negativo
TAXA_MAXIMA = 10_000.0  # taxa absurda → quase certamente um erro de escrita


def _validar_juros(capital, rate, time):
    """Valida os inputs comuns aos juros simples e compostos."""
    ensure_non_negative(capital, "capital (C)")
    if time < 0:
        raise OpError("O tempo não pode ser negativo.")
    if rate <= TAXA_MINIMA:
        raise OpError(
            f"A taxa tem de ser superior a {fmt(TAXA_MINIMA)}% "
            "(abaixo disso o montante seria negativo)."
        )
    if rate > TAXA_MAXIMA:
        raise OpError(f"A taxa parece incorreta: o máximo aceite é {fmt(TAXA_MAXIMA)}%.")


@op(
    "fin.simples",
    "financas",
    "Juros simples",
    "J = C · i · t  →  Montante = C + J. A taxa é aplicada apenas sobre o capital inicial.",
    [
        {"name": "capital", "label": "Capital (C)", "type": "number", "placeholder": "ex: 1000"},
        {"name": "rate", "label": "Taxa ao período (%)", "type": "number", "placeholder": "ex: 5"},
        {"name": "time", "label": "Tempo (n.º de períodos)", "type": "number", "placeholder": "ex: 3"},
    ],
    order=1,
)
def juros_simples(capital, rate, time):
    _validar_juros(capital, rate, time)
    taxa = rate / 100
    juros = capital * taxa * time
    montante = capital + juros
    return {
        "display": f"Montante = {fmt(montante)}  (Juros J = {fmt(juros)})",
        "steps": [
            f"i = {fmt(rate)} ÷ 100 = {fmt(taxa)}",
            f"J = C × i × t = {fmt(capital)} × {fmt(taxa)} × {fmt(time)} = {fmt(juros)}",
            f"M = C + J = {fmt(capital)} + {fmt(juros)} = {fmt(montante)}",
        ],
        "details": [
            {"label": "Capital inicial", "value": fmt(capital)},
            {"label": "Juros", "value": fmt(juros)},
            {"label": "Montante", "value": fmt(montante)},
        ],
    }


@op(
    "fin.composto",
    "financas",
    "Juros compostos",
    "M = C · (1 + i)ᵗ. Os juros incidem também sobre os juros acumulados.",
    [
        {"name": "capital", "label": "Capital (C)", "type": "number", "placeholder": "ex: 1000"},
        {"name": "rate", "label": "Taxa ao período (%)", "type": "number", "placeholder": "ex: 5"},
        {"name": "time", "label": "Tempo (n.º de períodos)", "type": "number", "placeholder": "ex: 3"},
    ],
    order=2,
)
def juros_compostos(capital, rate, time):
    _validar_juros(capital, rate, time)
    taxa = rate / 100
    try:
        montante = capital * (1 + taxa) ** time
    except OverflowError:
        raise OpError("Resultado demasiado grande.")
    juros = montante - capital

    steps = [
        f"i = {fmt(rate)} ÷ 100 = {fmt(taxa)}",
        f"M = {fmt(capital)} × (1 + {fmt(taxa)})^{fmt(time)} = {fmt(montante)}",
        f"J = M − C = {fmt(montante)} − {fmt(capital)} = {fmt(juros)}",
    ]

    # Simula os primeiros períodos (até 6) para mostrar o crescimento
    if float(time).is_integer() and 0 < int(time) <= 6:
        acumulado = capital
        linha = []
        for periodo in range(1, int(time) + 1):
            acumulado *= 1 + taxa
            linha.append(f"Período {periodo}: {fmt(acumulado)}")
        steps.append("Evolução → " + " | ".join(linha))

    return {
        "display": f"Montante = {fmt(montante)}  (Juros J = {fmt(juros)})",
        "steps": steps,
        "details": [
            {"label": "Capital inicial", "value": fmt(capital)},
            {"label": "Juros acumulados", "value": fmt(juros)},
            {"label": "Montante", "value": fmt(montante)},
        ],
    }
