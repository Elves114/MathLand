"""Operações sobre números: MDC/MMC, primos, fatoração e bases."""

import math

from ops.helpers import OpError, fmt
from ops.registry import op

SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
SUBSCRIPT = {2: "₂", 8: "₈", 10: "₁₀", 16: "₁₆"}


def _fatores_primos(n):
    """Devolve [(primo, expoente), ...]."""
    fatores = []
    restante = n
    divisor = 2
    while divisor * divisor <= restante:
        if restante % divisor == 0:
            expoente = 0
            while restante % divisor == 0:
                restante //= divisor
                expoente += 1
            fatores.append((divisor, expoente))
        # Passo dos divisores: 2 → 3 e, a partir daí, só ímpares (3, 5, 7, ...).
        if divisor == 2:
            divisor = 3
        else:
            divisor += 2
    if restante > 1:
        fatores.append((restante, 1))
    return fatores


@op(
    "num.mdc",
    "numeros",
    "Máximo divisor comum (MDC)",
    "Maior número que divide exatamente ambos os números.",
    [
        {"name": "a", "label": "1.º número", "type": "integer", "placeholder": "ex: 48"},
        {"name": "b", "label": "2.º número", "type": "integer", "placeholder": "ex: 18"},
    ],
    order=1,
)
def mdc(a, b):
    resultado = math.gcd(abs(a), abs(b))
    steps = [
        f"Divisões sucessivas ou Euclides: MDC({abs(a)}, {abs(b)}) = {resultado}",
        f"Verificação: {abs(a)} ÷ {resultado} = {abs(a) // resultado}  |  {abs(b)} ÷ {resultado} = {abs(b) // resultado}",
    ]
    if resultado == 1:
        steps.append("Os números são primos entre si (MDC = 1).")
    return {"display": f"MDC({a}, {b}) = {resultado}", "steps": steps}


@op(
    "num.mmc",
    "numeros",
    "Mínimo múltiplo comum (MMC)",
    "Menor número múltiplo comum de ambos os números.",
    [
        {"name": "a", "label": "1.º número", "type": "integer", "placeholder": "ex: 48"},
        {"name": "b", "label": "2.º número", "type": "integer", "placeholder": "ex: 18"},
    ],
    order=2,
)
def mmc(a, b):
    if a == 0 or b == 0:
        return {"display": f"MMC({a}, {b}) = 0", "steps": ["MMC com zero é 0 por convenção."]}
    divisor = math.gcd(abs(a), abs(b))
    resultado = abs(a * b) // divisor
    steps = [
        f"MMC(a, b) = |a × b| ÷ MDC(a, b)",
        f"MDC({abs(a)}, {abs(b)}) = {divisor}",
        f"MMC = {abs(a * b)} ÷ {divisor} = {resultado}",
    ]
    return {"display": f"MMC({a}, {b}) = {resultado}", "steps": steps}


@op(
    "num.primo",
    "numeros",
    "É número primo?",
    "Testa se um número é primo e mostra como foi verificado.",
    [
        {"name": "n", "label": "Número", "type": "integer", "placeholder": "ex: 97"},
    ],
    order=3,
)
def eh_primo(n):
    if n < 2:
        return {
            "display": f"{n} não é primo (números primos são ≥ 2).",
            "steps": [f"{n} < 2 → não é primo."],
        }

    limite = int(math.sqrt(n)) + 1
    divisor_encontrado = None
    for candidato in range(2, limite):
        if n % candidato == 0:
            divisor_encontrado = candidato
            break

    if divisor_encontrado is None:
        return {
            "display": f"{n} é primo ✓",
            "steps": [
                f"Testámos divisores de 2 até √{n} = {int(math.sqrt(n))} — nenhum divide {n}.",
                f"{n} tem exatamente 2 divisores: 1 e {n}.",
            ],
        }

    return {
        "display": f"{n} não é primo (divisível por {divisor_encontrado}).",
        "steps": [
            f"{n} ÷ {divisor_encontrado} = {n // divisor_encontrado}",
            f"{n} = {divisor_encontrado} × {n // divisor_encontrado}",
        ],
    }


@op(
    "num.fatoracao",
    "numeros",
    "Fatoração em números primos",
    "Decompõe um número na multiplicação dos seus fatores primos.",
    [
        {"name": "n", "label": "Número", "type": "integer", "placeholder": "ex: 360"},
    ],
    order=4,
)
def fatoracao(n):
    if n < 1:
        raise OpError("Introduza um número inteiro ≥ 1.")
    if n == 1:
        return {
            "display": "1 = 1 (unidade, não tem fatores primos)",
            "steps": ["O número 1 é a unidade multiplicative — não é primo nem composto."],
        }

    fatores = _fatores_primos(n)
    expressao = " × ".join(
        f"{primo}{str(expoente_).translate(SUPERSCRIPT) if expoente_ > 1 else ''}"
        for primo, expoente_ in fatores
    )
    verificacao = math.prod(primo**expoente_ for primo, expoente_ in fatores)
    return {
        "display": f"{n} = {expressao}",
        "steps": [
            "Divisões sucessivas por primos: "
            + " → ".join(
                f"dividir por {primo} ({expoente_}x)" for primo, expoente_ in fatores
            ),
            f"Verificação: {expressao} = {verificacao} ✓",
        ],
    }


@op(
    "num.analise",
    "numeros",
    "Análise de um número",
    "Paridade, dígitos, soma dos dígitos, testes de divisibilidade e primalidade.",
    [
        {"name": "n", "label": "Número", "type": "integer", "placeholder": "ex: 2340"},
    ],
    order=5,
)
def analise_numero(n):
    digitos = [int(d) for d in str(abs(n))]
    soma = sum(digitos)
    primo = eh_primo(n)["display"]

    def divisivel_por(divisor):
        return "sim" if n % divisor == 0 else "não"

    details = [
        {"label": "Paridade", "value": "par" if n % 2 == 0 else "ímpar"},
        {"label": "N.º de dígitos", "value": str(len(digitos))},
        {"label": "Soma dos dígitos", "value": fmt(soma)},
        {"label": "Divisível por 2", "value": divisivel_por(2)},
        {"label": "Divisível por 3", "value": divisivel_por(3)},
        {"label": "Divisível por 4", "value": divisivel_por(4)},
        {"label": "Divisível por 5", "value": divisivel_por(5)},
        {"label": "Divisível por 6", "value": divisivel_por(6)},
        {"label": "Divisível por 9", "value": divisivel_por(9)},
        {"label": "Divisível por 10", "value": divisivel_por(10)},
        {"label": "Primalidade", "value": primo},
    ]

    steps = [
        f"Dígitos: {' '.join(str(d) for d in digitos)}  |  Soma = {soma}",
        f"Divisível por 3? Soma dos dígitos {soma} é "
        f"{'múltiplo de 3' if soma % 3 == 0 else 'não múltiplo de 3'} → "
        f"{n} {'é' if n % 3 == 0 else 'não é'} divisível por 3.",
        f"Divisível por 9? {soma} {'é' if soma % 9 == 0 else 'não é'} múltiplo de 9.",
        f"Último dígito {digitos[-1]} → {'é' if n % 5 == 0 else 'não é'} divisível por 5.",
        primo,
    ]

    return {
        "display": f"{n}: {'par' if n % 2 == 0 else 'ímpar'}, {len(digitos)} dígitos, soma = {soma}",
        "steps": steps,
        "details": details,
    }


@op(
    "num.bases",
    "numeros",
    "Conversão de bases",
    "Converte um número entre as bases 2 (binário), 8 (octal), 10 (decimal) e 16 (hexadecimal).",
    [
        {"name": "value", "label": "Número", "type": "text", "placeholder": "ex: 1011 ou FF", "hint": "Sem o prefixo da base."},
        {
            "name": "from_base",
            "label": "Base de origem",
            "type": "select",
            "options": [
                {"value": "2", "label": "2 — Binário"},
                {"value": "8", "label": "8 — Octal"},
                {"value": "10", "label": "10 — Decimal"},
                {"value": "16", "label": "16 — Hexadecimal"},
            ],
        },
        {
            "name": "to_base",
            "label": "Base de destino",
            "type": "select",
            "options": [
                {"value": "2", "label": "2 — Binário"},
                {"value": "8", "label": "8 — Octal"},
                {"value": "10", "label": "10 — Decimal"},
                {"value": "16", "label": "16 — Hexadecimal"},
            ],
        },
    ],
    order=6,
)
def conversao_bases(value, from_base, to_base):
    texto = str(value).strip().upper()
    if not texto:
        raise OpError("O campo 'Número' não pode estar vazio.")

    base_origem = int(from_base)
    base_destino = int(to_base)

    try:
        decimal = int(texto, base_origem)
    except ValueError:
        raise OpError(f"'{texto}' não é um número válido na base {base_origem}.")

    digitos = "0123456789ABCDEF"
    if decimal == 0:
        convertido = "0"
    else:
        negativo = decimal < 0
        valor = abs(decimal)
        convertido = ""
        while valor > 0:
            convertido = digitos[valor % base_destino] + convertido
            valor //= base_destino
        if negativo:
            convertido = "-" + convertido

    sufixo_origem = SUBSCRIPT.get(base_origem, str(base_origem))
    sufixo_destino = SUBSCRIPT.get(base_destino, str(base_destino))

    steps = [
        f"Para decimal: {texto}{sufixo_origem} = {decimal}",
        f"Converter {decimal} para base {base_destino} por divisões sucessivas → {convertido}",
    ]
    if base_origem == 16 or base_destino == 16:
        steps.append("Hexadecimal: 0-9 e depois A=10, B=11, C=12, D=13, E=14, F=15.")
    if base_origem == 2 or base_destino == 2:
        steps.append("Binário: apenas os algarismos 0 e 1.")

    return {
        "display": f"{texto}{sufixo_origem} = {convertido}{sufixo_destino}  (decimal: {decimal})",
        "steps": steps,
        "details": [
            {"label": "Valor decimal", "value": str(decimal)},
            {"label": f"Base {base_destino}", "value": convertido},
        ],
    }
