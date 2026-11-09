"""Operações de estatística descritiva."""

from collections import Counter

from ops.helpers import OpError, fmt
from ops.registry import op


@op(
    "est.descritivas",
    "estatistica",
    "Estatísticas descritivas",
    "Calcula média, mediana, moda, amplitude, variância e desvio padrão de um conjunto de dados.",
    [
        {
            "name": "valores",
            "label": "Dados",
            "type": "list",
            "placeholder": "ex: 4, 8, 6, 4, 2, 9, 4",
            "hint": "Separe os valores por vírgula, ponto e vírgula ou espaço.",
        },
    ],
    order=1,
)
def estatisticas_descritivas(valores):
    dados = sorted(valores)
    n = len(dados)
    if n == 1:
        raise OpError("Introduza pelo menos 2 valores para calcular estatísticas.")

    soma = sum(dados)
    media = soma / n
    mediana = dados[n // 2] if n % 2 else (dados[n // 2 - 1] + dados[n // 2]) / 2
    amplitude = dados[-1] - dados[0]

    contagem = Counter(dados)
    frequencia_max = max(contagem.values())
    modas = sorted(value for value, count in contagem.items() if count == frequencia_max)
    if frequencia_max == 1:
        texto_moda = "sem moda (todos os valores aparecem 1 vez)"
        steps_moda = ["Não há valor repetido → não há moda (ou é chamada de 'amodal')."]
    else:
        texto_moda = ", ".join(fmt(m) for m in modas)
        steps_moda = [
            f"Frequências: " + ", ".join(f"{fmt(v)} → {c}x" for v, c in sorted(contagem.items())),
            f"Maior frequência = {frequencia_max} → moda: {texto_moda}",
        ]

    if n > 1:
        var_pop = sum((x - media) ** 2 for x in dados) / n
        var_amostra = sum((x - media) ** 2 for x in dados) / (n - 1)
        desvio_pop = var_pop**0.5
        desvio_amostra = var_amostra**0.5
    else:  # pragma: no cover - o caso n == 1 é bloqueado acima
        var_pop = var_amostra = desvio_pop = desvio_amostra = 0.0

    steps = [
        f"Soma Σx = {fmt(soma)}  |  n = {n}",
        f"Média = Σx ÷ n = {fmt(soma)} ÷ {n} = {fmt(media)}",
        f"Ordenados: {', '.join(fmt(v) for v in dados)}",
        (
            f"Mediana = valor central = {fmt(mediana)}"
            if n % 2
            else f"Mediana = média dos dois centrais ({fmt(dados[n // 2 - 1])} e {fmt(dados[n // 2])}) = {fmt(mediana)}"
        ),
        *steps_moda,
        f"Amplitude = máx − mín = {fmt(dados[-1])} − {fmt(dados[0])} = {fmt(amplitude)}",
        f"Variância (população) σ² = Σ(x − média)² ÷ n = {fmt(var_pop)}",
        f"Desvio padrão σ = √{fmt(var_pop)} = {fmt(desvio_pop)}",
    ]
    if n > 1:
        steps.append(
            f"Amostra: s² = Σ(x − média)² ÷ (n−1) = {fmt(var_amostra)}  →  s = {fmt(desvio_amostra)}"
        )

    return {
        "display": f"Média = {fmt(media)}  |  Mediana = {fmt(mediana)}  |  Moda = {texto_moda}",
        "steps": steps,
        "details": [
            {"label": "Quantidade (n)", "value": str(n)},
            {"label": "Soma (Σx)", "value": fmt(soma)},
            {"label": "Média", "value": fmt(media)},
            {"label": "Mediana", "value": fmt(mediana)},
            {"label": "Moda", "value": texto_moda},
            {"label": "Amplitude", "value": fmt(amplitude)},
            {"label": "Variância (σ²)", "value": fmt(var_pop)},
            {"label": "Desvio padrão (σ)", "value": fmt(desvio_pop)},
            {"label": "Desvio amostral (s)", "value": fmt(desvio_amostra) if n > 1 else "—"},
        ],
    }


@op(
    "est.ponderada",
    "estatistica",
    "Média ponderada",
    "Média em que cada valor tem um peso diferente (ex.: notas com créditos).",
    [
        {
            "name": "valores",
            "label": "Valores",
            "type": "list",
            "placeholder": "ex: 16, 14, 12",
            "hint": "Separe por vírgula.",
        },
        {
            "name": "pesos",
            "label": "Pesos",
            "type": "list",
            "placeholder": "ex: 6, 4, 2",
            "hint": "Mesma quantidade de pesos que de valores.",
        },
    ],
    order=2,
)
def media_ponderada(valores, pesos):
    if len(valores) != len(pesos):
        raise OpError(
            f"Há {len(valores)} valores e {len(pesos)} pesos — têm de ser a mesma quantidade."
        )
    if any(peso < 0 for peso in pesos):
        raise OpError("Os pesos não podem ser negativos.")
    soma_pesos = sum(pesos)
    if soma_pesos == 0:
        raise OpError("A soma dos pesos não pode ser zero.")

    produto = sum(v * p for v, p in zip(valores, pesos))
    media = produto / soma_pesos

    return {
        "display": f"Média ponderada = {fmt(media)}",
        "steps": [
            "Σ(valores × pesos) = "
            + " + ".join(f"{fmt(v)}×{fmt(p)}" for v, p in zip(valores, pesos))
            + f" = {fmt(produto)}",
            f"Σ(pesos) = {fmt(soma_pesos)}",
            f"Média = {fmt(produto)} ÷ {fmt(soma_pesos)} = {fmt(media)}",
        ],
        "details": [
            {"label": "Soma dos produtos", "value": fmt(produto)},
            {"label": "Soma dos pesos", "value": fmt(soma_pesos)},
            {"label": "Média ponderada", "value": fmt(media)},
        ],
    }
