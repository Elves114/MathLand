"""Teste de fumo em pytest: valida que todas as operações registadas executam,
que existe um caso de teste para cada uma e que os campos batem certo com as
assinaturas das funções.

Substitui o antigo `backend/tests/smoke_test.py` (executado à mão).
"""

import inspect
import re

import pytest

from ops.registry import CATEGORIES, OPERATIONS, get_operation, sorted_operations

CASOS = {
    # aritmética
    "arit.soma": {"a": 12.5, "b": 7},
    "arit.subtracao": {"a": 20, "b": 8},
    "arit.multiplicacao": {"a": 6, "b": 4},
    "arit.divisao": {"a": 10, "b": 4},
    "arit.potencia": {"base": 2, "exp": 10},
    "arit.raiz": {"n": 144},
    "arit.expressao": {"expression": "(3 + 5) * 2^3 / sqrt(16)"},
    # frações
    "frac.soma": {"a": "1/2", "b": "1/3"},
    "frac.subtracao": {"a": "3/4", "b": "1/6"},
    "frac.multiplicacao": {"a": "2/3", "b": "5/7"},
    "frac.divisao": {"a": "3/5", "b": "2/9"},
    "frac.simplificar": {"value": "36/48"},
    "frac.decimal_para_fracao": {"value": "0.75"},
    "frac.para_decimal": {"a": "5/8"},
    "frac.misto": {"value": "2 3/4"},
    # porcentagem
    "pct.valor": {"percent": 20, "value": 150},
    "pct.aumento": {"value": 250, "percent": 23},
    "pct.desconto": {"value": 250, "percent": 15},
    "pct.taxa": {"part": 30, "whole": 150},
    "pct.variacao": {"from_value": 80, "to_value": 100},
    # finanças
    "fin.simples": {"capital": 1000, "rate": 5, "time": 3},
    "fin.composto": {"capital": 1000, "rate": 5, "time": 3},
    # álgebra
    "alg.linear": {"a": 2, "b": 4, "c": 10},
    "alg.quadratica": {"a": 1, "b": -5, "c": 6},
    "alg.sistema": {"a1": 1, "b1": 1, "c1": 5, "a2": 2, "b2": -1, "c2": 1},
    "alg.funcao": {"expression": "x^2 + 3*x - 5", "x": 4},
    # matrizes
    "mat.determinante": {"linha1": [1, 2], "linha2": [3, 4], "linha3": None},
    "mat.soma": {
        "a1": [1, 2], "a2": [3, 4], "a3": None,
        "b1": [10, 20], "b2": [30, 40], "b3": None,
    },
    "mat.multiplicacao": {
        "a1": [1, 2], "a2": [3, 4], "a3": None,
        "b1": [10, 20], "b2": [30, 40], "b3": None,
    },
    # geometria
    "geo.retangulo": {"base": 8, "altura": 5},
    "geo.quadrado": {"lado": 6},
    "geo.triangulo_area": {"base": 10, "altura": 6},
    "geo.triangulo_lados": {"a": 7, "b": 8, "c": 9},
    "geo.circulo": {"raio": 5},
    "geo.trapezio": {"base1": 12, "base2": 7, "altura": 5},
    "geo.losango": {"d1": 10, "d2": 6, "lado": 5},
    "geo.paralelogramo": {"base": 10, "altura": 6, "lado": 7},
    "geo.pitagoras": {"a": 3, "b": 4, "c": None},
    "geo.distancia": {"x1": 1, "y1": 2, "x2": 4, "y2": 6},
    "geo.cubo": {"lado": 3},
    "geo.cilindro": {"raio": 4, "altura": 10},
    "geo.cone": {"raio": 3, "altura": 4},
    "geo.esfera": {"raio": 6},
    # trigonometria
    "trig.funcao": {"funcao": "sen", "angulo": 30, "unidade": "graus"},
    "trig.retangulo": {"hipotenusa": 10, "angulo": 30},
    "trig.lei_senos": {"a": 8, "angulo_A": 60, "angulo_B": 45},
    # progressões
    "prog.pa": {"a1": 3, "razao": 5, "n": 20},
    "prog.pg": {"a1": 2, "razao": 3, "n": 5},
    # logaritmos
    "log.base": {"base": 2, "value": 32},
    "log.inverso": {"base": 10, "logaritmo": 2.5},
    # estatística
    "est.descritivas": {"valores": [4, 8, 6, 4, 2, 9, 4]},
    "est.ponderada": {"valores": [16, 14, 12], "pesos": [6, 4, 2]},
    # probabilidade
    "prob.evento": {"favoraveis": 3, "possiveis": 8},
    "prob.combinacoes": {"n": 5, "k": 3},
    "prob.independentes": {"pa": 0.6, "pb": 0.5},
    # razão e proporção
    "raz.simples": {"a": 48, "b": 18},
    "raz.regra3": {"a": 3, "b": 12, "c": 7},
    "raz.escala": {"scale": "1:50000", "distance": 4, "direction": "mapa_para_real"},
    "raz.media_proporcional": {"a": 4, "b": 9},
    # números
    "num.mdc": {"a": 48, "b": 18},
    "num.mmc": {"a": 48, "b": 18},
    "num.primo": {"n": 97},
    "num.fatoracao": {"n": 360},
    "num.analise": {"n": 2340},
    "num.bases": {"value": "1011", "from_base": "2", "to_base": "10"},
    # criptografia (curvas elípticas)
    "ecc.validar": {"a": 0, "b": 7, "p": 79, "x": 1, "y": 18},
    "ecc.soma": {"a": 0, "b": 7, "p": 79, "x1": 1, "y1": 18, "x2": 6, "y2": 12},
    "ecc.multiplicacao": {"a": 0, "b": 7, "p": 79, "x": 1, "y": 18, "k": 13},
    "ecc.inverso": {"a": 0, "b": 7, "p": 79, "x1": 1, "y1": 18, "x2": 29, "y2": 8},
    # unidades
    "un.comprimento": {"value": 2.5, "de": "km", "para": "m"},
    "un.massa": {"value": 750, "de": "g", "para": "kg"},
    "un.temperatura": {"value": 25, "de": "C", "para": "F"},
}


def test_todas_as_operacoes_tem_caso_de_teste():
    faltam = set(OPERATIONS) - set(CASOS)
    assert not faltam, f"Operações sem caso de teste: {sorted(faltam)}"


def test_casos_sem_operacao_correspondente():
    orfas = set(CASOS) - set(OPERATIONS)
    assert not orfas, f"Casos de teste sem operação: {sorted(orfas)}"


@pytest.mark.parametrize("op_id", sorted(CASOS))
def test_caso_executa_sem_excecao(op_id, run_op):
    resultado = run_op(op_id, **CASOS[op_id])
    assert isinstance(resultado, dict), f"{op_id} devolveu {type(resultado)}"
    assert resultado.get("display"), f"{op_id} sem display"


def test_ids_seguem_o_padrao_categoria_acao():
    """Regressão do id 'frac_para_decimal' (devia ser 'frac.para_decimal')."""
    padrao = re.compile(r"^[a-z]+\.[a-z0-9_]+$")
    fora = [op_id for op_id in OPERATIONS if not padrao.match(op_id)]
    assert not fora, f"IDs fora do padrão categoria.acao: {fora}"


def test_id_legado_continua_funcional():
    assert "frac_para_decimal" not in OPERATIONS
    assert get_operation("frac_para_decimal") is get_operation("frac.para_decimal")
    assert get_operation("frac.para_decimal") is not None
    assert get_operation("nao.existe") is None


def test_campos_compatíveis_com_a_assinatura():
    """Cada campo do formulário tem de existir como parâmetro da função e vice-versa.

    Apanga bugs como os campos 'from'/'to' das unidades, que não coincidiam
    com os parâmetros from_unit/to_unit da função.
    """
    for op_id, definition in sorted(OPERATIONS.items()):
        parametros = inspect.signature(definition["fn"]).parameters
        campos = {field["name"] for field in definition["fields"]}

        sem_parametro = campos - set(parametros)
        assert not sem_parametro, (
            f"{op_id}: campos sem parâmetro correspondente: {sorted(sem_parametro)}"
        )

        obrigatorios = {
            name
            for name, param in parametros.items()
            if param.default is inspect.Parameter.empty
        }
        sem_campo = obrigatorios - campos
        assert not sem_campo, (
            f"{op_id}: parâmetros obrigatórios sem campo no formulário: {sorted(sem_campo)}"
        )


def test_categorias_sem_operacoes_nem_duplicadas():
    ids = [category_id for category_id, _, _ in CATEGORIES]
    assert len(ids) == len(set(ids))
    categorias_usadas = {operation["category"] for operation in OPERATIONS.values()}
    assert categorias_usadas <= set(ids), (
        f"Categorias usadas sem entrada em CATEGORIES: {categorias_usadas - set(ids)}"
    )


def test_sorted_operations_ordenado_e_com_cache():
    lista = sorted_operations()
    assert len(lista) == len(OPERATIONS)
    # lru_cache: chamadas repetidas devolvem o mesmo objeto
    assert sorted_operations() is lista
    # e a ordem respeita a ordem das categorias
    ordem = [category_id for category_id, _, _ in CATEGORIES]
    indices = [ordem.index(item["category"]) for item in lista]
    assert indices == sorted(indices)
