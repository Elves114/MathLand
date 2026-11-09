# 🧮 MathLab — Calculadora de Matemática (básico → intermediário)

Aplicação **fullstack** para cálculos de múltiplas matérias da matemática, do básico ao
intermediário.

- **Backend:** Python + [Flask](https://flask.palletsprojects.com/) (API REST)
- **Frontend:** HTML + CSS + JavaScript **puros** (sem frameworks)
- **Localização:** `/home/Correia/Developer/fullstack/projetos random/primeiro/MathLand/calculadora-matematica`

---

## 🚀 Como arrancar

### Linux / macOS

```bash
./start.sh
```

### Windows

```bat
start.bat
```

### Manualmente (qualquer sistema)

```bash
# 1) ambiente virtual + dependências
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows: .venv\Scripts\pip install -r requirements.txt

# 2) arrancar o servidor
.venv/bin/python backend/app.py                  # Windows: .venv\Scripts\python backend\app.py
```

Depois abre **http://127.0.0.1:5000** no navegador.

### Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `PORT` | `5000` | Porta do servidor (ex.: `PORT=8080 ./start.sh`) |
| `HOST` | `127.0.0.1` | Use `HOST=0.0.0.0` para aceder pela rede local |
| `FLASK_DEBUG` | `1` | `0` desativa o modo debug |

> ⚠️ **Modo debug / produção:** por omissão o Flask arranca com `FLASK_DEBUG=1`
> (recarregamento automático e depuração) — aceitável apenas para uso local e
> educacional. **Nunca exponha o servidor com debug ativo em produção**;
> defina `FLASK_DEBUG=0` e corra atrás de um servidor WSGI (gunicorn, uWSGI…).

---

## ✅ Funcionalidades

**16 matérias · 72 operações**, todas com explicação passo-a-passo do cálculo.

| Matéria | Operações |
|---|---|
| **Aritmética** | soma, subtração, multiplicação, divisão, potência, raiz quadrada, avaliar expressão (com `sqrt`, `log`, `sin`, `pi`…) |
| **Frações** | somar, subtrair, multiplicar, dividir, simplificar, decimal→fração, fração→decimal, número misto→fração |
| **Porcentagem** | % de um valor, aumento, desconto, "que % é", variação percentual |
| **Finanças** | juros simples, juros compostos (com evolução período a período) |
| **Álgebra** | equação 1.º grau, equação 2.º grau (Bhaskara), sistema 2×2 (Cramer), calcular f(x) |
| **Matrizes** | determinante (2×2 e 3×3), soma e multiplicação de matrizes |
| **Geometria** | retângulo, quadrado, triângulo (base/altura e 3 lados por Heron), círculo, trapézio, losango, paralelogramo, Pitágoras, distância entre pontos, cubo, cilindro, cone, esfera |
| **Trigonometria** | seno/cosseno/tangente (graus e radianos), triângulo retângulo, lei dos senos |
| **Progressões** | progressão aritmética e geométrica (n-ésimo termo e soma) |
| **Logaritmos** | logaritmo de base livre, equação logarítmica |
| **Estatística** | média, mediana, moda, amplitude, variância, desvio padrão (populacional e amostral), média ponderada |
| **Probabilidade** | probabilidade de um evento, permutações e combinações, eventos independentes |
| **Razão e Proporção** | simplificar razão, regra de três, escala gráfica, média proporcional |
| **Números** | MDC, MMC, é primo?, fatoração em primos, análise do número (paridade, divisibilidade…), conversão de bases (2, 8, 10, 16) |
| **Criptografia** | curvas elípticas: ponto na curva (e contagem \|E(Fp)\|), soma de pontos, multiplicação escalar k·P (direto, double-and-add) e logaritmo discreto k tal que k·P = Q (inverso, baby-step giant-step) |
| **Unidades** | conversão de comprimento, massa e temperatura |

Extras do front:

- 🔎 **Pesquisa global** de operações (atalho `/`)
- 📱 Design responsivo (desktop, tablet e telemóvel)
- 🧠 A última matéria visitada fica guardada (`localStorage`)
- ⌨️ `Esc` fecha o modal, `Enter` calcula
- 🇵🇹 Aceita **vírgula decimal** (`12,5`) e **frações** (`1/2`, `1 1/2`) nos campos numéricos
- ✅ **Validação local** dos campos antes de enviar ao servidor (mensagem em português, foco no campo inválido)
- ♿ **Acessibilidade:** foco preso dentro do modal (`Tab` não escapa), devolução do foco ao cartão ao fechar, resultado anunciado por leitores de tela (`aria-live`)

---

## 📁 Estrutura do projeto

```
calculadora-matematica/
├── backend/
│   ├── app.py                  # API Flask + servidor do frontend
│   ├── ops/                    # pacote com todas as operações matemáticas
│   │   ├── registry.py         # registo de categorias e operações (com cache)
│   │   ├── helpers.py          # validação, formatação e avaliador seguro de expressões
│   │   ├── arithmetic.py       # aritmética básica
│   │   ├── fractions_ops.py    # frações
│   │   ├── percent.py          # porcentagem
│   │   ├── finance.py          # juros (com validação de capital/taxa)
│   │   ├── algebra.py          # equações e sistemas
│   │   ├── matrices.py         # determinante, soma e multiplicação
│   │   ├── geometry.py         # áreas, perímetros, volumes
│   │   ├── trigonometry.py     # seno/cosseno, triângulo, lei dos senos
│   │   ├── sequences.py        # progressões (PA e PG)
│   │   ├── logarithms.py       # logaritmos
│   │   ├── stats.py            # estatística
│   │   ├── probability.py      # probabilidade, combinações
│   │   ├── ratio.py            # razão e proporção
│   │   ├── numbers.py          # primos, MDC/MMC, bases
│   │   ├── elliptic.py         # curvas elípticas (ECC): validação, soma, k·P e log. discreto
│   │   └── units.py            # conversão de unidades
│   └── tests/                  # suite pytest
│       ├── conftest.py         # fixtures (app, client, run_op, detalhe)
│       ├── test_smoke.py       # cobre as 72 operações + compatibilidade campos/assinatura
│       ├── test_api.py         # endpoints Flask (test_client)
│       └── test_ops_*.py       # testes unitários por domínio (inclui test_ops_cripto.py)
├── frontend/
│   ├── index.html              # estrutura da aplicação
│   ├── styles.css              # estilos (CSS puro)
│   └── app.js                  # lógica: catálogo, formulários, validação e resultados
├── pytest.ini                  # configuração do pytest
├── requirements.txt            # dependências de produção (pinadas)
├── requirements-dev.txt        # + pytest, para desenvolvimento
├── start.sh                    # arranque rápido (Linux/macOS)
├── start.bat                   # arranque rápido (Windows)
└── README.md
```

---

## 🔌 API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/operations` | Catálogo de categorias e operações (o front constrói os formulários a partir daqui) |
| `POST` | `/api/calculate` | Calcula uma operação |
| `GET` | `/` | Página da aplicação |

Exemplo:

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
     -H "Content-Type: application/json" \
     -d '{"id": "alg.quadratica", "inputs": {"a": 1, "b": -3, "c": -4}}'
```

```json
{
  "ok": true,
  "result": {
    "display": "Duas soluções reais: x₁ = -1  |  x₂ = 4",
    "steps": ["Δ = b² − 4ac = (-3)² − 4(1)(-4) = 25", "…"],
    "details": [{"label": "x₁", "value": "-1"}, {"label": "x₂", "value": "4"}]
  }
}
```

Erros devolvem `400` com `{"ok": false, "error": "mensagem em português"}`.

---

## ➕ Como adicionar uma nova operação

Basta criar uma função no módulo adequado de `backend/ops/` e usar o decorador `op` —
o backend expõe-a na API e o front desenha o formulário sozinho:

```python
# backend/ops/arithmetic.py
from ops.registry import op
from ops.helpers import fmt

@op(
    "arit.porcentagem_dupla",          # id único
    "aritmetica",                      # categoria (tem de existir em registry.py)
    "Porcentagem sucessiva",           # nome apresentado
    "Aplica duas percentagens seguidas.",
    [                                  # campos → geram os inputs no front
        {"name": "value", "label": "Valor", "type": "number", "placeholder": "ex: 100"},
        {"name": "p1", "label": "1.ª %", "type": "number", "placeholder": "ex: 10"},
    ],
    order=8,                           # posição na lista
)
def porcentagem_dupla(value, p1):
    resultado = value * (1 + p1 / 100)
    return {
        "display": f"{fmt(value)} → {fmt(resultado)}",
        "steps": [f"{fmt(value)} × (1 + {fmt(p1 / 100)}) = {fmt(resultado)}"],
    }
```

Tipos de campo disponíveis: `number`, `integer`, `text`, `fraction`, `list`,
`expression`, `select` (com `options`) — e `"required": False` para campos opcionais.

> Os nomes dos campos **têm de coincidir com os parâmetros da função** — há um
> teste (`test_campos_compatíveis_com_a_assinatura`) que garante isso
> automaticamente.

---

## 🧪 Testes

```bash
# instalar dependências de desenvolvimento (uma vez)
.venv/bin/pip install -r requirements-dev.txt

# correr a suite completa (257 testes)
.venv/bin/pytest

# apenas um domínio / ficheiro
.venv/bin/pytest backend/tests/test_ops_algebra.py
.venv/bin/pytest -k "quadratica or sistema"
```

A suite cobre:

- **testes unitários por domínio** (`test_ops_*.py`) com asserções de valores
  esperados (ex.: `sistema_2x2(1,1,5,2,-1,1)` → x=2, y=3) e casos-limite
  (divisão por zero, Δ < 0, triângulo inválido, capital negativo, `1/0`…);
- **testes de API** com o `test_client` do Flask (`test_api.py`):
  catálogo, cálculo, erros 400/404 e id legado `frac_para_decimal`;
- **teste de fumo** (`test_smoke.py`): executa as 72 operações com um caso de
  exemplo cada, garante que não falta nenhum caso e que os campos dos
  formulários batem certo com as assinaturas das funções (`inspect.signature`);
- **estrutura**: IDs no padrão `categoria.acao`, categorias válidas e cache de
  `sorted_operations()`.

---

## 🔒 Nota de segurança

As expressões introduzidas pelo utilizador são avaliadas por um **avaliador próprio
construído sobre `ast`** (`backend/ops/helpers.py`): não usa `eval()` nem executa
qualquer código arbitrário — só números, operadores, constantes e funções matemáticas
da lista permitida.
