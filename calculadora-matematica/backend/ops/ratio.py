"""Operações de razão e proporção."""

import math

from ops.helpers import OpError, decimal_places, fmt, to_number
from ops.registry import op

# Evita 10**N gigante com números minúsculos (ex.: 5e-324 → 324 casas)
MAX_CASAS_DECIMAIS = 18


@op(
    "raz.simples",
    "razao",
    "Simplificar razão",
    "Simplifica uma razão a : b para os menores termos possíveis.",
    [
        {"name": "a", "label": "1.º termo (a)", "type": "number", "placeholder": "ex: 48"},
        {"name": "b", "label": "2.º termo (b)", "type": "number", "placeholder": "ex: 18"},
    ],
    order=1,
)
def razao_simples(a, b):
    if a == 0 and b == 0:
        raise OpError("A razão 0 : 0 não está definida.")
    if abs(a - round(a)) > 1e-9 or abs(b - round(b)) > 1e-9:
        # Permite decimais: multiplica pelos dois valores até ficar com inteiros.
        # decimal_places() usa Decimal(str(x)), por isso 1e-05 conta 5 casas
        # (com str(a).split(".") daria 0 casas e a razão ficaria errada).
        casas = min(
            MAX_CASAS_DECIMAIS,
            max(decimal_places(a), decimal_places(b)),
        )
        escala = 10**casas
        a_i, b_i = int(round(a * escala)), int(round(b * escala))
    else:
        a_i, b_i = int(round(a)), int(round(b))

    divisor = math.gcd(a_i, b_i) or 1
    final_a, final_b = a_i // divisor, b_i // divisor
    if final_b < 0 or (final_b == 0 and final_a < 0):
        final_a, final_b = -final_a, -final_b

    steps = [
        f"MDC({abs(a_i)}, {abs(b_i)}) = {divisor}",
        f"{a_i} ÷ {divisor} = {final_a}  |  {b_i} ÷ {divisor} = {final_b}",
        f"Razão simplificada: {final_a} : {final_b}",
    ]
    return {
        "display": f"{fmt(a)} : {fmt(b)} = {final_a} : {final_b}",
        "steps": steps,
        "details": [
            {"label": "Razão", "value": f"{final_a} : {final_b}"},
            {"label": "Valor da razão", "value": fmt(final_a / final_b) if final_b else "—"},
        ],
    }


@op(
    "raz.regra3",
    "razao",
    "Regra de três simples",
    "Se a está para b, quanto está para c?  x = (b × c) ÷ a.",
    [
        {"name": "a", "label": "1.º valor (origem)", "type": "number", "placeholder": "ex: 3"},
        {"name": "b", "label": "2.º valor (correspondente)", "type": "number", "placeholder": "ex: 12"},
        {"name": "c", "label": "3.º valor (a procurar)", "type": "number", "placeholder": "ex: 7"},
    ],
    order=2,
)
def regra_de_tres(a, b, c):
    if a == 0:
        raise OpError("O primeiro valor não pode ser zero (divisão por zero).")
    x = b * c / a
    return {
        "display": f"{fmt(a)} → {fmt(b)}  então  {fmt(c)} → {fmt(x)}",
        "steps": [
            f"Proporção: {fmt(a)} / {fmt(b)} = {fmt(c)} / x",
            f"x = ({fmt(b)} × {fmt(c)}) ÷ {fmt(a)} = {fmt(b * c)} ÷ {fmt(a)} = {fmt(x)}",
        ],
        "details": [{"label": "Resultado (x)", "value": fmt(x)}],
    }


@op(
    "raz.escala",
    "razao",
    "Escala gráfica",
    "Converte distâncias entre o mapa e a realidade usando uma escala do tipo 1:50000.",
    [
        {
            "name": "scale",
            "label": "Escala",
            "type": "text",
            "placeholder": "ex: 1:50000",
            "hint": "Formato: 1:X (também aceita 1/50000).",
        },
        {"name": "distance", "label": "Distância", "type": "number", "placeholder": "ex: 4"},
        {
            "name": "direction",
            "label": "Converter de",
            "type": "select",
            "options": [
                {"value": "mapa_para_real", "label": "Mapa → Realidade"},
                {"value": "real_para_mapa", "label": "Realidade → Mapa"},
            ],
        },
    ],
    order=3,
)
def escala(scale, distance, direction):
    texto = str(scale).strip().replace(",", ".").replace("/", ":")
    if ":" not in texto:
        raise OpError("Escreva a escala no formato 1:50000.")
    esquerda, _, direita = texto.partition(":")
    try:
        base = to_number(esquerda, "escala (parte esquerda)")
        fator = to_number(direita, "escala (parte direita)")
    except OpError:
        raise OpError(f"Escala inválida: {scale}. Use o formato 1:50000.")
    if base == 0 or fator == 0:
        raise OpError("Os valores da escala não podem ser zero.")

    razao = fator / base  # unidades reais por unidade no mapa

    if direction == "mapa_para_real":
        resultado = distance * razao
        steps = [
            f"Escala {texto}: 1 unidade no mapa = {fmt(razao)} unidades na realidade",
            f"{fmt(distance)} × {fmt(razao)} = {fmt(resultado)}",
        ]
        display = f"{fmt(distance)} no mapa = {fmt(resultado)} na realidade"
    else:
        if razao == 0:  # pragma: no cover
            raise OpError("Escala inválida.")
        resultado = distance / razao
        steps = [
            f"Escala {texto}: 1 unidade no mapa = {fmt(razao)} unidades na realidade",
            f"{fmt(distance)} ÷ {fmt(razao)} = {fmt(resultado)}",
        ]
        display = f"{fmt(distance)} na realidade = {fmt(resultado)} no mapa"

    return {
        "display": display,
        "steps": steps,
        "details": [
            {"label": "Escala", "value": texto},
            {"label": "Resultado", "value": fmt(resultado)},
        ],
    }


@op(
    "raz.media_proporcional",
    "razao",
    "Média proporcional",
    "Encontra x tal que a : x = x : b  (x = √(a · b)).",
    [
        {"name": "a", "label": "1.º valor (a)", "type": "number", "placeholder": "ex: 4"},
        {"name": "b", "label": "2.º valor (b)", "type": "number", "placeholder": "ex: 9"},
    ],
    order=4,
)
def media_proporcional(a, b):
    if a * b < 0:
        raise OpError("O produto a · b não pode ser negativo para ter média proporcional real.")
    x = math.sqrt(a * b)
    return {
        "display": f"x = √({fmt(a)} × {fmt(b)}) = √{fmt(a * b)} = {fmt(x)}",
        "steps": [
            f"Proporção: {fmt(a)} / x = x / {fmt(b)}",
            f"x² = a × b = {fmt(a * b)}",
            f"x = √{fmt(a * b)} = {fmt(x)}",
        ],
        "details": [{"label": "Média proporcional (x)", "value": fmt(x)}],
    }
