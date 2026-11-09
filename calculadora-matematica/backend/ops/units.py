"""Conversão de unidades: comprimento, massa e temperatura."""

from ops.helpers import OpError, ensure_non_negative, fmt
from ops.registry import op

# Fatores em unidades de base (metros e quilogramas)
COMPRIMENTO = {
    "mm": (0.001, "milímetro"),
    "cm": (0.01, "centímetro"),
    "m": (1.0, "metro"),
    "km": (1000.0, "quilómetro"),
    "in": (0.0254, "polegada"),
    "ft": (0.3048, "pé"),
    "yd": (0.9144, "jarda"),
    "mi": (1609.344, "milha"),
    "nmi": (1852.0, "milha náutica"),
}

MASSA = {
    "mg": (1e-6, "miligrama"),
    "g": (0.001, "grama"),
    "kg": (1.0, "quilograma"),
    "t": (1000.0, "tonelada"),
    "oz": (0.028349523125, "onça"),
    "lb": (0.45359237, "libra"),
}

TEMPERATURA = {"C": "Celsius", "F": "Fahrenheit", "K": "Kelvin"}

ZERO_ABSOLUTO = -273.15  # °C


def _opcoes(tabela):
    return [
        {"value": sigla, "label": f"{sigla} — {nome}"}
        for sigla, (_fator, nome) in tabela.items()
    ]


def _opcoes_temperatura():
    return [
        {"value": sigla, "label": f"{sigla} — {nome}"}
        for sigla, nome in TEMPERATURA.items()
    ]


def _converter(valor, tabela, de, para):
    if de not in tabela:
        raise OpError(f"Unidade de origem inválida: {de}.")
    if para not in tabela:
        raise OpError(f"Unidade de destino inválida: {para}.")
    fator_de = tabela[de][0]
    fator_para = tabela[para][0]
    base = valor * fator_de  # valor na unidade de base
    return base / fator_para, fator_de, fator_para


@op(
    "un.comprimento",
    "unidades",
    "Conversão de comprimento",
    "Converte entre milímetros, centímetros, metros, quilómetros, polegadas, pés, jardas, milhas e milhas náuticas.",
    [
        {"name": "value", "label": "Valor", "type": "number", "placeholder": "ex: 2.5"},
        {"name": "de", "label": "De", "type": "select", "options": _opcoes(COMPRIMENTO)},
        {"name": "para", "label": "Para", "type": "select", "options": _opcoes(COMPRIMENTO)},
    ],
    order=1,
)
def converter_comprimento(value, de, para):
    resultado, fator_de, fator_para = _converter(value, COMPRIMENTO, de, para)

    steps = [
        f"{fmt(value)} {de} = {fmt(value)} × {fmt(fator_de)} (metros) = {fmt(value * fator_de)} m",
        f"{fmt(value * fator_de)} m ÷ {fmt(fator_para)} = {fmt(resultado)} {para}",
    ]
    if de == para:
        steps.append("Origem e destino são a mesma unidade — o valor não muda.")

    return {
        "display": f"{fmt(value)} {de} = {fmt(resultado)} {para}",
        "steps": steps,
        "details": [
            {"label": "Valor original", "value": f"{fmt(value)} {de}"},
            {"label": "Valor convertido", "value": f"{fmt(resultado)} {para}"},
            {"label": "Em metros", "value": f"{fmt(value * fator_de)} m"},
        ],
    }


@op(
    "un.massa",
    "unidades",
    "Conversão de massa",
    "Converte entre miligramas, gramas, quilogramas, toneladas, onças e libras.",
    [
        {"name": "value", "label": "Valor", "type": "number", "placeholder": "ex: 750"},
        {"name": "de", "label": "De", "type": "select", "options": _opcoes(MASSA)},
        {"name": "para", "label": "Para", "type": "select", "options": _opcoes(MASSA)},
    ],
    order=2,
)
def converter_massa(value, de, para):
    resultado, fator_de, fator_para = _converter(value, MASSA, de, para)

    steps = [
        f"{fmt(value)} {de} = {fmt(value)} × {fmt(fator_de)} (kg) = {fmt(value * fator_de)} kg",
        f"{fmt(value * fator_de)} kg ÷ {fmt(fator_para)} = {fmt(resultado)} {para}",
    ]
    if de == para:
        steps.append("Origem e destino são a mesma unidade — o valor não muda.")

    return {
        "display": f"{fmt(value)} {de} = {fmt(resultado)} {para}",
        "steps": steps,
        "details": [
            {"label": "Valor original", "value": f"{fmt(value)} {de}"},
            {"label": "Valor convertido", "value": f"{fmt(resultado)} {para}"},
            {"label": "Em quilogramas", "value": f"{fmt(value * fator_de)} kg"},
        ],
    }


def _para_celsius(valor, unidade):
    if unidade == "C":
        return valor
    if unidade == "F":
        return (valor - 32) * 5 / 9
    ensure_non_negative(valor, "temperatura em Kelvin")  # K < 0 é fisicamente impossível
    return valor - 273.15


def _de_celsius(celsius, unidade):
    if unidade == "C":
        return celsius
    if unidade == "F":
        return celsius * 9 / 5 + 32
    return celsius + 273.15


@op(
    "un.temperatura",
    "unidades",
    "Conversão de temperatura",
    "Converte entre graus Celsius (°C), graus Fahrenheit (°F) e Kelvin (K).",
    [
        {"name": "value", "label": "Valor", "type": "number", "placeholder": "ex: 25"},
        {
            "name": "de",
            "label": "De",
            "type": "select",
            "options": _opcoes_temperatura(),
        },
        {
            "name": "para",
            "label": "Para",
            "type": "select",
            "options": _opcoes_temperatura(),
        },
    ],
    order=3,
)
def converter_temperatura(value, de, para):
    if de not in TEMPERATURA:
        raise OpError(f"Unidade de origem inválida: {de}.")
    if para not in TEMPERATURA:
        raise OpError(f"Unidade de destino inválida: {para}.")

    celsius = _para_celsius(value, de)
    if celsius < ZERO_ABSOLUTO - 1e-9:
        raise OpError(
            f"A temperatura não pode ser inferior ao zero absoluto "
            f"({fmt(ZERO_ABSOLUTO)} °C = 0 K)."
        )
    resultado = _de_celsius(celsius, para)

    steps = [
        f"Passar por Celsius: {fmt(value)} {de} = {fmt(celsius)} °C",
        f"Converter para {para}: {fmt(celsius)} °C = {fmt(resultado)} {para}",
        "Fórmulas: °F = °C × 9/5 + 32  |  K = °C + 273,15  |  °C = (°F − 32) × 5/9",
    ]
    if de == para:
        steps.append("Origem e destino são a mesma unidade — o valor não muda.")

    return {
        "display": f"{fmt(value)} {de} = {fmt(resultado)} {para}",
        "steps": steps,
        "details": [
            {"label": "Celsius (°C)", "value": f"{fmt(celsius)} °C"},
            {"label": "Fahrenheit (°F)", "value": f"{fmt(_de_celsius(celsius, 'F'))} °F"},
            {"label": "Kelvin (K)", "value": f"{fmt(_de_celsius(celsius, 'K'))} K"},
        ],
    }
