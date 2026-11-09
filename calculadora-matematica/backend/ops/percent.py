"""Operações de percentagem."""

from ops.helpers import OpError, fmt
from ops.registry import op


@op(
    "pct.valor",
    "porcentagem",
    "Percentagem de um valor",
    "Quanto é p% de um valor? (ex.: 20% de 150)",
    [
        {"name": "percent", "label": "Percentagem (%)", "type": "number", "placeholder": "ex: 20"},
        {"name": "value", "label": "Valor", "type": "number", "placeholder": "ex: 150"},
    ],
    order=1,
)
def percentagem_de_valor(percent, value):
    fracao = percent / 100
    resultado = fracao * value
    return {
        "display": f"{fmt(percent)}% de {fmt(value)} = {fmt(resultado)}",
        "steps": [
            f"{fmt(percent)} ÷ 100 = {fmt(fracao)}",
            f"{fmt(fracao)} × {fmt(value)} = {fmt(resultado)}",
        ],
    }


@op(
    "pct.aumento",
    "porcentagem",
    "Aumento percentual",
    "Aplica um aumento de p% a um valor (ex.: IVA, inflação).",
    [
        {"name": "value", "label": "Valor original", "type": "number", "placeholder": "ex: 250"},
        {"name": "percent", "label": "Aumento (%)", "type": "number", "placeholder": "ex: 23"},
    ],
    order=2,
)
def aumento(value, percent):
    aumento_valor = value * percent / 100
    resultado = value + aumento_valor
    return {
        "display": f"{fmt(value)} com aumento de {fmt(percent)}% = {fmt(resultado)}",
        "steps": [
            f"Aumento: {fmt(value)} × {fmt(percent)} ÷ 100 = {fmt(aumento_valor)}",
            f"Novo valor: {fmt(value)} + {fmt(aumento_valor)} = {fmt(resultado)}",
        ],
    }


@op(
    "pct.desconto",
    "porcentagem",
    "Desconto percentual",
    "Aplica um desconto de p% a um valor (ex.: promoções).",
    [
        {"name": "value", "label": "Valor original", "type": "number", "placeholder": "ex: 250"},
        {"name": "percent", "label": "Desconto (%)", "type": "number", "placeholder": "ex: 15"},
    ],
    order=3,
)
def desconto(value, percent):
    if percent < 0 or percent > 100:
        raise OpError("O desconto deve estar entre 0% e 100%.")
    desconto_valor = value * percent / 100
    resultado = value - desconto_valor
    return {
        "display": f"{fmt(value)} com desconto de {fmt(percent)}% = {fmt(resultado)}",
        "steps": [
            f"Desconto: {fmt(value)} × {fmt(percent)} ÷ 100 = {fmt(desconto_valor)}",
            f"Novo valor: {fmt(value)} − {fmt(desconto_valor)} = {fmt(resultado)}",
            f"Poupança: {fmt(desconto_valor)}",
        ],
    }


@op(
    "pct.taxa",
    "porcentagem",
    "Que percentagem é?",
    "Descobre a percentagem que uma parte representa do todo (ex.: 30 é quanto % de 150?).",
    [
        {"name": "part", "label": "Parte", "type": "number", "placeholder": "ex: 30"},
        {"name": "whole", "label": "Total", "type": "number", "placeholder": "ex: 150"},
    ],
    order=4,
)
def que_percentagem(part, whole):
    if whole == 0:
        raise OpError("O total não pode ser zero.")
    percent = part / whole * 100
    return {
        "display": f"{fmt(part)} é {fmt(percent)}% de {fmt(whole)}",
        "steps": [f"{fmt(part)} ÷ {fmt(whole)} = {fmt(part / whole)}", f"{fmt(part / whole)} × 100 = {fmt(percent)}%"],
    }


@op(
    "pct.variacao",
    "porcentagem",
    "Variação percentual",
    "Variação percentual entre dois valores (crescimento ou decrescimento).",
    [
        {"name": "from_value", "label": "Valor inicial", "type": "number", "placeholder": "ex: 80"},
        {"name": "to_value", "label": "Valor final", "type": "number", "placeholder": "ex: 100"},
    ],
    order=5,
)
def variacao(from_value, to_value):
    if from_value == 0:
        raise OpError("O valor inicial não pode ser zero (divisão por zero).")
    diferenca = to_value - from_value
    percent = diferenca / from_value * 100
    if abs(percent) < 1e-12:
        situacao = "não houve variação"
    elif percent > 0:
        situacao = f"aumento de {fmt(abs(percent))}%"
    else:
        situacao = f"descida de {fmt(abs(percent))}%"
    return {
        "display": f"De {fmt(from_value)} para {fmt(to_value)}: {situacao}",
        "steps": [
            f"Diferença: {fmt(to_value)} − {fmt(from_value)} = {fmt(diferenca)}",
            f"{fmt(diferenca)} ÷ {fmt(from_value)} × 100 = {fmt(percent)}%",
        ],
    }
