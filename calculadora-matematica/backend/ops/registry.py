"""Registo central das operações matemáticas.

Cada módulo de matemática (aritmética, geometria, ...) usa o decorador `op`
para se registar aqui. O backend expõe o catálogo via API e o frontend
renderiza os formulários a partir desse catálogo.
"""

from collections import OrderedDict
from functools import lru_cache

# Ordem das categorias apresentadas no frontend
CATEGORIES = [
    ("aritmetica", "Aritmética", "Operações básicas, potências, raízes e expressões numéricas."),
    ("fracoes", "Frações", "Soma, subtração, simplificação e conversão de frações."),
    ("porcentagem", "Porcentagem", "Percentagens, aumentos, descontos e variações."),
    ("financas", "Finanças", "Juros simples e juros compostos."),
    ("algebra", "Álgebra", "Equações do 1.º e 2.º grau, sistemas e funções."),
    ("matrizes", "Matrizes", "Determinante, soma e multiplicação de matrizes."),
    ("geometria", "Geometria", "Áreas, perímetros, volumes, distâncias e o Teorema de Pitágoras."),
    ("trigonometria", "Trigonometria", "Seno, cosseno, triângulo retângulo e lei dos senos."),
    ("progressoes", "Progressões", "Progressões aritméticas e geométricas."),
    ("logaritmos", "Logaritmos", "Logaritmo de base livre e equações logarítmicas."),
    ("estatistica", "Estatística", "Média, mediana, moda, variância e desvio padrão."),
    ("probabilidade", "Probabilidade", "Eventos, permutações, combinações e eventos independentes."),
    ("razao", "Razão e Proporção", "Razões, regras de três, escalas e médias proporcionais."),
    ("numeros", "Números", "Divisibilidade, números primos, MDC/MMC e mudança de base."),
    ("criptografia", "Criptografia", "Curvas elípticas: validação de pontos, soma, multiplicação escalar (direto) e logaritmo discreto (inverso)."),
    ("unidades", "Unidades", "Conversão de comprimento, massa e temperatura."),
]

OPERATIONS: "OrderedDict[str, dict]" = OrderedDict()

# IDs antigos aceites pela API por compatibilidade (o catálogo usa os novos)
LEGACY_IDS = {
    "frac_para_decimal": "frac.para_decimal",
}


def op(op_id, category, name, description, fields, order=0):
    """Regista uma operação e devolve a função original."""

    if category not in {cid for cid, _, _ in CATEGORIES}:
        raise ValueError(f"Categoria desconhecida: {category}")

    def decorator(fn):
        OPERATIONS[op_id] = {
            "id": op_id,
            "category": category,
            "name": name,
            "description": description,
            "fields": fields,
            "order": order,
            "fn": fn,
        }
        sorted_operations.cache_clear()  # invalida a lista ordenada em cache
        return fn

    return decorator


def get_operation(op_id):
    """Procura uma operação pelo id (aceita também ids antigos)."""
    return OPERATIONS.get(op_id) or OPERATIONS.get(LEGACY_IDS.get(op_id, ""))


@lru_cache(maxsize=1)
def sorted_operations():
    """Devolve as operações ordenadas por categoria e ordem interna.

    Cacheada (as operações são registadas no arranque, no import dos módulos);
    `op()` limpa o cache sempre que uma operação nova é registada.
    """
    category_order = {cid: index for index, (cid, _, _) in enumerate(CATEGORIES)}
    return sorted(
        OPERATIONS.values(),
        key=lambda item: (
            category_order[item["category"]],
            item["order"],
            item["name"].lower(),
        ),
    )
