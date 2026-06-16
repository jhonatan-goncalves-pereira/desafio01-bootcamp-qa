# 🚀 ServeRest API Test Automation

Projeto de automação de testes de API desenvolvido com Python, Pytest e Requests para
validação dos principais fluxos da API ServeRest.

> Desafio desenvolvido durante o Bootcamp QA da Compass UOL (AI/R Fellowship).

![Tests](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/actions/workflows/tests.yml/badge.svg)

---

## 📋 Sumário

- [Objetivo](#-objetivo)
- [API Utilizada](#-api-utilizada)
- [Estratégia de Branches](#-estratégia-de-branches)
- [Stack](#️-stack)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Arquitetura](#-arquitetura)
- [Instalação](#️-instalação)
- [Executando os Testes](#️-executando-os-testes)
- [Análise de Cobertura](#-análise-de-cobertura)
- [Bugs Encontrados e Reportados](#-bugs-encontrados-e-reportados)
- [Melhorias Identificadas](#-melhorias-identificadas)
- [Cobertura por Módulo](#-cobertura-por-módulo)
- [Allure Reports](#-allure-reports)
- [Extras Implementados](#-extras-implementados)
- [Allure Reports](#-allure-reports)
- [Estatísticas](#-estatísticas)
- [Boas Práticas Aplicadas](#-boas-práticas-aplicadas)

---

## 🎯 Objetivo

Garantir a qualidade dos principais endpoints da API através de testes automatizados cobrindo:

- Fluxos positivos (Happy Path)
- Validações de regras de negócio
- Cenários negativos e de borda
- Testes exploratórios para descoberta de bugs
- Regressão de bugs encontrados
- Validação de estrutura de resposta via JSON Schema

---

## 🌐 API Utilizada

**ServeRest** — API pública para estudos e automação de testes.

Base URL: https://compassuol.serverest.dev  
Swagger: https://compassuol.serverest.dev/swagger.json?lang=pt-BR

---

## 🌿 Estratégia de Branches

```
main                                          ← produção estável
└── develop                                   ← integração contínua
    ├── feature/bug-report-e-melhorias        ← bug reports + melhorias iniciais
    ├── feature/readme-sumario-cobertura-detalhada  ← sumário e análise de cobertura
    └── feature/melhorias-m02-m05             ← implementação de M02 e M05
```

| Branch | Propósito |
|---|---|
| `main` | Código estável, entregável final |
| `develop` | Integração de features antes de ir para main |
| `feature/bug-report-e-melhorias` | Bug reports documentados + melhorias iniciais identificadas |
| `feature/readme-sumario-cobertura-detalhada` | Sumário no README + análise de cobertura pelos 8 critérios |
| `feature/melhorias-m02-m05` | Implementação de C15 (carrinho sem token) e U21 (excluir usuário com carrinho) |
| `feature/allure-reports` | Integração do Allure Framework: decoradores, CI e documentação |

---

## 🛠️ Stack

| Ferramenta | Versão | Finalidade |
|---|---|---|
| Python | 3.10+ | Linguagem base |
| Pytest | 7.4.3 | Framework de testes |
| Requests | 2.31.0 | Chamadas HTTP |
| jsonschema | 4.23.0 | Validação de estrutura JSON |
| pytest-html | 4.1.1 | Relatório HTML |
| pytest-timeout | 2.4.0 | Timeout por teste (60s) |
| allure-pytest | 2.13.5 | Relatório Allure interativo |
| GitHub Actions | — | CI/CD automático |

---

## 📂 Estrutura do Projeto

```text
desafio01-bootcamp-qa/
│
├── .github/
│   └── workflows/
│       └── tests.yml          ← GitHub Actions CI (main, develop, feature/**)
│
├── helpers/
│   ├── carrinho_helper.py
│   ├── generators.py
│   ├── login_helper.py        ← timeout de 10s no POST /login
│   ├── produtos_helper.py
│   └── usuarios_helper.py
│
├── tests/
│   ├── test_carrinho.py       ← 15 testes
│   ├── test_login.py          ← 7 testes
│   ├── test_produtos.py       ← 20 testes
│   └── test_usuarios.py       ← 21 testes
│
├── allure-results/        ← gerado automaticamente (gitignored)
├── allure.properties          ← metadata do ambiente para o report
├── conftest.py                ← fixtures com estratégia de auth robusta
├── PLANO-DE-TESTES.md
├── pytest.ini                 ← timeout=60s configurado
├── README.md
└── requirements.txt
```

---

## 🧠 Arquitetura

### Helpers
Centralizam chamadas HTTP. Cada módulo corresponde a um endpoint da API.

### Generators
Geram dados dinâmicos com UUID — sem hardcode de e-mails, nomes ou IDs.

### Fixtures (`conftest.py`)

| Fixture | Escopo | Responsabilidade |
|---|---|---|
| `base_url` | session | URL base da API |
| `usuario_payload` | function | Payload dinâmico para criação |
| `usuario_criado` | function | Usuário real persistido + teardown com restauração |
| `token_admin` | session | Token JWT do administrador (reutilizado na sessão) |
| `token_nao_admin` | function | Token JWT de não-admin via rebaixamento temporário |
| `produto_criado` | function | Cria produto + teardown automático |

> **Nota sobre a instância:** `compassuol.serverest.dev` só permite login
> para o usuário pré-existente. As fixtures contornam essa limitação sem
> alterar os arquivos de teste.

---

## ⚙️ Instalação

```bash
git clone https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa
cd desafio01-bootcamp-qa

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## ▶️ Executando os Testes

```bash
pytest                                           # suíte completa
pytest -v                                        # modo detalhado
pytest tests/test_login.py -v                   # só login
pytest tests/test_produtos.py -v                # só produtos
pytest tests/test_usuarios.py -v                # só usuários
pytest tests/test_carrinho.py -v                # só carrinho
pytest --html=report.html --self-contained-html  # com relatório HTML
pytest -k "BUG" -v                              # só testes de regressão de bugs
```

---

## 📊 Análise de Cobertura

> O planejamento completo da suíte está em **[PLANO-DE-TESTES.md](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/blob/main/PLANO-DE-TESTES.md)**.

### Método utilizado

Cobertura calculada conforme os critérios definidos no artigo
[Como verificar a cobertura de testes da API REST](https://medium.com/revista-dtar/como-verificar-a-cobertura-de-testes-da-api-rest-9e2f745564b)
(Nayara Crema, Revista DTAR, 2020), que define **8 critérios** baseados em
*Input Coverage* e *Output Coverage*.

---

### 1. Path Coverage (Input)

Mede quantas URIs únicas da API estão cobertas (independente do método HTTP).

A ServeRest possui **9 paths** únicos:

| URI | Coberta? |
|---|---|
| `/login` | ✅ |
| `/usuarios` | ✅ |
| `/usuarios/{id}` | ✅ |
| `/produtos` | ✅ |
| `/produtos/{id}` | ✅ |
| `/carrinhos` | ✅ |
| `/carrinhos/{id}` | ✅ |
| `/carrinhos/cancelar-compra` | ✅ |
| `/carrinhos/concluir-compra` | ✅ |

**Path Coverage = 9/9 = 100%**

---

### 2. Operator Coverage (Input)

Mede quantas operações (par `URI + método HTTP`) estão cobertas.

| Endpoint | Método | Coberta? |
|---|---|---|
| `/login` | POST | ✅ |
| `/usuarios` | GET | ✅ |
| `/usuarios` | POST | ✅ |
| `/usuarios/{id}` | GET | ✅ |
| `/usuarios/{id}` | PUT | ✅ |
| `/usuarios/{id}` | DELETE | ✅ |
| `/produtos` | GET | ✅ |
| `/produtos` | POST | ✅ |
| `/produtos/{id}` | GET | ✅ |
| `/produtos/{id}` | PUT | ✅ |
| `/produtos/{id}` | DELETE | ✅ |
| `/carrinhos` | GET | ✅ |
| `/carrinhos` | POST | ✅ |
| `/carrinhos/{id}` | GET | ✅ |
| `/carrinhos/cancelar-compra` | DELETE | ✅ |
| `/carrinhos/concluir-compra` | DELETE | ✅ |

**Operator Coverage = 16/16 = 100%**

---

### 3. Parameter Coverage (Input)

Mede se cada parâmetro de cada operação foi exercitado pelo menos uma vez.
Inclui parâmetros de query, path e body.

| Operação | Parâmetro | Coberto? |
|---|---|---|
| `POST /login` | `email` | ✅ |
| `POST /login` | `password` | ✅ |
| `GET /usuarios` | `_id` (query) | ✅ (via filtro email) |
| `GET /usuarios` | `nome` (query) | ❌ não testado diretamente |
| `GET /usuarios` | `email` (query) | ✅ |
| `GET /usuarios` | `password` (query) | ❌ não testado |
| `GET /usuarios` | `administrador` (query) | ✅ |
| `POST /usuarios` | `nome`, `email`, `password`, `administrador` | ✅ |
| `GET /usuarios/{id}` | `id` (path) | ✅ |
| `PUT /usuarios/{id}` | `id` (path) + body completo | ✅ |
| `DELETE /usuarios/{id}` | `id` (path) | ✅ |
| `GET /produtos` | `nome` (query) | ✅ |
| `GET /produtos` | `_id`, `preco`, `descricao`, `quantidade` (query) | ❌ não testados |
| `POST /produtos` | `nome`, `preco`, `descricao`, `quantidade` | ✅ |
| `GET /produtos/{id}` | `id` (path) | ✅ |
| `PUT /produtos/{id}` | `id` (path) + body completo | ✅ |
| `DELETE /produtos/{id}` | `id` (path) | ✅ |
| `GET /carrinhos` | `_id`, `idUsuario`, `precoTotal`, `quantidadeTotal` (query) | ❌ nenhum filtro testado |
| `POST /carrinhos` | `produtos[].idProduto`, `produtos[].quantidade` | ✅ |
| `GET /carrinhos/{id}` | `id` (path) | ✅ |
| `DELETE /cancelar-compra` | token (header) | ✅ |
| `DELETE /concluir-compra` | token (header) | ✅ |

Parâmetros totais mapeados: **~30** | Cobertos: **~24**

**Parameter Coverage ≈ 24/30 = 80%**

> Parâmetros fora: filtros de query em `GET /usuarios` (nome, password), filtros de query em `GET /carrinhos` (idUsuario, precoTotal, quantidadeTotal) e filtros adicionais de `GET /produtos`.

---

### 4. Parameter Value Coverage (Input)

Mede se parâmetros booleanos e enum assumiram todos os valores possíveis.

| Parâmetro | Valores possíveis | Valores testados |
|---|---|---|
| `administrador` (POST/PUT `/usuarios`) | `"true"`, `"false"` | `"true"` ✅, `"false"` ✅ |
| `administrador` (GET `/usuarios` query) | `"true"`, `"false"` | `"true"` ✅, `"false"` ❌ |

**Parameter Value Coverage = 3/4 = 75%**

> Fora: filtro `?administrador=false` em `GET /usuarios` não foi testado explicitamente.

---

### 5. Content-Type Coverage (Input e Output)

A ServeRest aceita e retorna exclusivamente `application/json`. A suíte usa `json=payload`
em todas as requisições (a lib `requests` define `Content-Type: application/json` automaticamente)
e valida bodies JSON em todos os testes.

**Content-Type Coverage = 100%**

---

### 6. Operation Flow Coverage (Input)

Mede fluxos encadeados de operações.

| Fluxo | Operações | Coberto? |
|---|---|---|
| F01 | POST /usuarios → POST /login → POST /produtos → DELETE /produtos | ✅ (fixtures) |
| F02 | POST /login → POST /carrinhos → DELETE /cancelar-compra | ✅ C10 |
| F03 | POST /login → POST /carrinhos → DELETE /concluir-compra | ✅ C11 |
| F04 | POST /produtos → POST /carrinhos → cancelar → verificar estoque restaurado | ✅ C14 |
| F05 | POST /produtos → DELETE /produtos com carrinho ativo → 400 | ✅ P20 |
| F06 | POST /usuarios → GET /usuarios/{id} | ✅ U14 |
| F07 | Criar produto → filtrar por nome no GET /produtos | ✅ P02 |
| F08 | POST /login → DELETE /concluir-compra (sem carrinho) | ✅ C12 |

**Operation Flow Coverage = 8/8 = 100%**

---

### 7. Response Properties Body Coverage (Output)

Mede se as propriedades do corpo da resposta estão sendo validadas. A suíte usa JSON Schema
em todas as respostas de listagem e busca, cobrindo todas as propriedades documentadas.

| Endpoint | Propriedades da resposta | Cobertas via JSON Schema |
|---|---|---|
| `POST /login` | `message`, `authorization` | ✅ `LOGIN_SUCESSO_SCHEMA` |
| `GET /usuarios` | `quantidade`, `usuarios[]` + todas as props do usuário | ✅ `LISTA_USUARIOS_SCHEMA` |
| `GET /usuarios/{id}` | `_id`, `nome`, `email`, `password`, `administrador` | ✅ `USUARIO_SCHEMA` |
| `GET /produtos` | `quantidade`, `produtos[]` + todas as props do produto | ✅ `LISTA_PRODUTOS_SCHEMA` |
| `GET /produtos/{id}` | `_id`, `nome`, `preco`, `descricao`, `quantidade` | ✅ `PRODUTO_SCHEMA` |
| `GET /carrinhos` | `quantidade`, `carrinhos[]` | ✅ `LISTA_CARRINHOS_SCHEMA` |
| `GET /carrinhos/{id}` | `_id`, `produtos[]`, `precoTotal`, `quantidadeTotal`, `idUsuario` | ✅ `CARRINHO_SCHEMA` |
| Respostas de erro | campo `message` | ✅ verificado com `assert "message" in body` |

**Response Properties Body Coverage = 100%**

---

### 8. Status Code Coverage (Output)

Mede quantos status codes possíveis por operação foram exercitados.

| Operação | Status codes possíveis | Cobertos |
|---|---|---|
| `POST /login` | 200, 400, 401 | ✅ 200, 400, 401 — **3/3** |
| `GET /usuarios` | 200, 400 | ✅ 200, 400 — **2/2** |
| `POST /usuarios` | 201, 400 | ✅ 201, 400 — **2/2** |
| `GET /usuarios/{id}` | 200, 400 | ✅ 200, 400 — **2/2** |
| `PUT /usuarios/{id}` | 200, 201, 400 | ✅ 200, 201, 400 — **3/3** |
| `DELETE /usuarios/{id}` | 200 | ✅ 200 — **1/1** |
| `GET /produtos` | 200, 400 | ✅ 200 — **1/2** ❌ 400 não testado |
| `POST /produtos` | 201, 400, 401, 403 | ✅ 201, 400, 401, 403 — **4/4** |
| `GET /produtos/{id}` | 200, 400 | ✅ 200, 400 — **2/2** |
| `PUT /produtos/{id}` | 200, 201, 400, 401, 403 | ✅ 200, 201, 400 — **3/5** ❌ 401, 403 não testados |
| `DELETE /produtos/{id}` | 200, 400, 401, 403 | ✅ 200, 400 — **2/4** ❌ 401, 403 não testados |
| `GET /carrinhos` | 200 | ✅ 200 — **1/1** |
| `POST /carrinhos` | 201, 400, 401 | ✅ 201, 400 — **2/3** ❌ 401 não testado |
| `GET /carrinhos/{id}` | 200, 400 | ✅ 200, 400 — **2/2** |
| `DELETE /cancelar-compra` | 200, 401 | ✅ 200 — **1/2** ❌ 401 não testado |
| `DELETE /concluir-compra` | 200, 401 | ✅ 200 — **1/2** ❌ 401 não testado |

Status codes totais mapeados: **39** | Cobertos: **32**

**Status Code Coverage = 32/39 ≈ 82%**

> Status codes fora: 400 em `GET /produtos`, 401/403 em `PUT` e `DELETE /produtos/{id}`, 401 em `POST /carrinhos`, 401 em ambos os DELETEs de carrinho.

---

### Resumo Geral de Cobertura

| Critério | Resultado |
|---|---|
| **Path Coverage** | **100%** (9/9) |
| **Operator Coverage** | **100%** (16/16) |
| **Parameter Coverage** | **~80%** (~24/30) |
| **Parameter Value Coverage** | **75%** (3/4) |
| **Content-Type Coverage** | **100%** |
| **Operation Flow Coverage** | **100%** (8/8) |
| **Response Properties Body Coverage** | **100%** |
| **Status Code Coverage** | **~82%** (32/39) |

**Cobertura média geral ≈ 92%**

### O que ficou fora e por quê

| Item | Motivo |
|---|---|
| Filtros de query em `GET /usuarios` (nome, password) | Parâmetros de uso raro; email e administrador são os filtros relevantes |
| Filtros de query em `GET /carrinhos` (idUsuario, precoTotal) | Identificado como melhoria M03 — baixa prioridade |
| `?administrador=false` em `GET /usuarios` | Comportamento implicitamente coberto; foi testado `true` e case-sensitive |
| 401/403 em `PUT` e `DELETE /produtos/{id}` | A instância compassuol é instável para múltiplos logins; priorizados os cenários de negócio |
| 401 em `POST /carrinhos` e DELETEs de carrinho | Mesmo motivo acima |
| 400 em `GET /produtos` | A API não documenta cenário de erro para listagem sem filtros inválidos |

---

## 🐛 Bugs Encontrados e Reportados

5 bugs encontrados durante a execução exploratória, reportados como **[Issues no GitHub](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/issues)** e documentados em detalhes no **[BUG-REPORTS.md](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/blob/main/BUG-REPORTS.md)**.

| # | Título | Severidade | Endpoints |
|---|---|---|---|
| BUG #1 | Contrato de erro inconsistente — `message` vs chave do campo | 🟡 Média | `/login`, `/usuarios`, `/produtos` |
| BUG #2 | Senhas retornadas em texto puro | 🔴 Crítica | `GET /usuarios`, `GET /usuarios/{id}` |
| BUG #3 | `quantidade=0` aceito no cadastro, inutilizável no carrinho | 🟡 Média | `POST /produtos` |
| BUG #4 | Campo `quantidade` aceita string numérica silenciosamente | 🟢 Baixa | `POST /produtos` |
| BUG #5 | DELETE sem carrinho ativo retorna 200 em vez de 404 | 🟢 Baixa | `DELETE /carrinhos/*` |

> Cada bug possui passos de reprodução, comportamento esperado vs. obtido e testes de regressão. Ver [BUG-REPORTS.md](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/blob/main/BUG-REPORTS.md).

---

## 💡 Melhorias Identificadas

Oportunidades de evolução mapeadas após análise de cobertura e execução exploratória. Detalhes completos, exemplos de implementação e estimativas de esforço em **[MELHORIAS.md](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/blob/main/MELHORIAS.md)**.

| # | Descrição | Área | Prioridade | Status |
|---|---|---|---|---|
| M01 | Validar `preco=0` no cadastro de produto | Produtos | 🟡 Média | Pendente |
| M02 | `POST /carrinhos` sem token → 401 | Carrinhos | 🟡 Média | ✅ Implementado (C15) |
| M03 | Filtro `GET /carrinhos?idUsuario=X` | Carrinhos | 🟢 Baixa | Pendente |
| M04 | Token JWT expirado → 401 | Auth | 🔴 Alta | Pendente |
| M05 | Excluir usuário com carrinho ativo → 400 | Usuários | 🔴 Alta | ✅ Implementado (U21) |
| M06 | Campos em branco (`""`) vs. campo ausente | Geral | 🟡 Média | Pendente |
| M07 | Parametrizar testes de campos obrigatórios | Refactor | 🟢 Baixa | Pendente |

---

## ✅ Cobertura por Módulo

### 🔐 Login (7 testes)

| ID | Cenário | Status |
|---|---|---|
| L01 | Credenciais válidas → 200 + token | ✅ |
| L02 | Token é JWT válido (3 partes) | ✅ |
| L03 | Senha incorreta → 401 | ✅ |
| L04 | E-mail inexistente → 401 | ✅ |
| L05 | E-mail vazio → 400 `[BUG #1]` | ✅ |
| L06 | Password vazio → 400 `[BUG #1]` | ✅ |
| L07 | Ambos vazios → 400 | ✅ |

### 👤 Usuários (21 testes)

| ID | Cenário | Status |
|---|---|---|
| U01–U02 | Listar → 200 + schema + `quantidade` correto | ✅ |
| U03–U04 | Filtros por `administrador` (true / case-sensitive) | ✅ |
| U05–U11 | Cadastro (válido, duplicado, campos ausentes, tipo errado) | ✅ |
| U12–U13 | Senha exposta em plaintext `[BUG #2]` | ✅ |
| U14–U16 | Busca por ID (válido, inexistente, formato inválido) | ✅ |
| U17–U18 | Atualizar (existente, upsert) | ✅ |
| U19–U20 | Excluir (existente, inexistente) | ✅ |
| U21 | Excluir com carrinho ativo → 400 `[M05]` | ✅ |

### 📦 Produtos (20 testes)

| ID | Cenário | Status |
|---|---|---|
| P01–P02 | Listar → 200 + schema + filtro por nome | ✅ |
| P03–P07 | Cadastro (admin, sem token, não-admin, duplicado, token inválido) | ✅ |
| P08–P09 | Bugs de validação de entrada `[BUG #3]` `[BUG #4]` | ✅ |
| P10–P12 | Validação de campos (preço float, negativo, qtd negativa) | ✅ |
| P13–P15 | Busca por ID (válido, formato inválido, inexistente) | ✅ |
| P16–P18 | Atualizar (existente, nome duplicado, upsert) | ✅ |
| P19–P20 | Excluir (sem/com carrinho ativo) | ✅ |

### 🛒 Carrinhos (15 testes)

| ID | Cenário | Status |
|---|---|---|
| C01–C03 | Listar + criar + validar schema | ✅ |
| C04–C07 | Restrições (2 carrinhos, produto inexistente, estoque, duplicado) | ✅ |
| C08–C09 | Buscar (existente, inexistente) | ✅ |
| C10–C11 | Cancelar e concluir com carrinho | ✅ |
| C12–C13 | Cancelar/concluir sem carrinho `[BUG #5]` | ✅ |
| C14 | Cancelar restaura estoque | ✅ |
| C15 | Criar sem token → 401 `[M02]` | ✅ |

---


---

## 📊 Allure Reports

O projeto conta com integração completa com o [Allure Framework](https://allurepy.readthedocs.io/), gerando relatórios HTML interativos com rastreabilidade total dos testes.

### O que o relatório exibe

| Dimensão | Detalhe |
|---|---|
| **Epic / Feature / Story** | Hierarquia de todos os 63 testes por módulo |
| **Severity** | BLOCKER, CRITICAL, NORMAL, MINOR por teste |
| **Steps** | Passos internos de cada teste (Arrange → Act → Assert) |
| **Attachments** | Response body JSON anexado nos testes de listagem |
| **Issues linkadas** | BUG #1 ao #5 linkados diretamente nos testes de regressão |
| **Tags** | smoke, 
egativo, positivo, orda, ug, seguranca |

### Gerar o relatório localmente

`ash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar os testes (gera a pasta allure-results/)
pytest

# 3. Instalar Allure CLI (necessário uma vez)
# macOS:  brew install allure
# Linux:  snap install allure
# Windows: scoop install allure

# 4. Abrir o relatório no browser
allure serve allure-results
`

> A pasta llure-results/ está no .gitignore. Apenas os resultados brutos são gerados localmente.

### Relatório no CI (GitHub Actions)

A cada push ou pull request, o workflow:
1. Executa os 63 testes com --alluredir=allure-results
2. Gera o relatório HTML estático com llure generate
3. Publica como **artefato** numerado por run (llure-report-N)

Para baixar: vá em **Actions → run desejada → Artifacts → allure-report-N**.


---

## 📊 Allure Reports

A suíte gera relatórios interativos com o [Allure Framework](https://docs.qameta.io/allure/), permitindo
visualizar resultados por módulo, severidade, tag e histórico de execuções.

### Como executar localmente

`ash
# 1. Instalar dependências (allure-pytest já incluído no requirements.txt)
pip install -r requirements.txt

# 2. Rodar os testes — os resultados são salvos em allure-results/
pytest

# 3. Gerar e abrir o relatório no browser
allure serve allure-results
`

> Para instalar o Allure CLI: https://docs.qameta.io/allure/#_installing_a_commandline

### Estrutura do relatório

Os testes são organizados com decoradores que geram uma hierarquia clara no relatório:

| Decorator | Valor | O que representa |
|---|---|---|
| @allure.epic | ServeRest API | Produto / sistema |
| @allure.feature | Login / Usuarios / Produtos / Carrinhos | Módulo da API |
| @allure.story | Listagem / Cadastro / Autenticacao... | Funcionalidade |
| @allure.severity | BLOCKER / CRITICAL / NORMAL / MINOR | Prioridade do teste |
| @allure.tag | smoke / negativo / bug / regressao... | Categoria livre |
| @allure.issue | #1 ao #5 | Link para bug reports |
| llure.step | Descrição de cada passo | Rastreabilidade AAA |
| llure.attach | Response body JSON | Evidência inline |

### No CI (GitHub Actions)

A cada push/PR, o workflow:
1. Executa os testes com --alluredir=allure-results
2. Gera o relatório HTML com llure generate
3. Publica como artefato numerado por run em **Actions → Artifacts**

`
allure-report-<run_number>/   ← relatório Allure completo
relatorio-html-<run_number>/  ← relatório pytest-html (legado)
`

### Extras Implementados

---

## 🔍 Extras Implementados

### Extra 1 — JSON Schema (todos os endpoints)

| Arquivo | Schemas validados |
|---|---|
| `test_login.py` | `LOGIN_SUCESSO_SCHEMA` |
| `test_usuarios.py` | `USUARIO_SCHEMA`, `LISTA_USUARIOS_SCHEMA` |
| `test_produtos.py` | `PRODUTO_SCHEMA`, `LISTA_PRODUTOS_SCHEMA` |
| `test_carrinho.py` | `CARRINHO_SCHEMA`, `LISTA_CARRINHOS_SCHEMA` |

### Extra 2 — GitHub Actions

Pipeline em `.github/workflows/tests.yml`:
- Executa em todo push e pull request para `main`, `develop` e `feature/**`
- Publica relatório HTML como artefato numerado por run

---

## 📈 Estatísticas

| Módulo | Testes | Bugs cobertos |
|---|---|---|
| Login | 7 | 1 |
| Usuários | 21 | 2 |
| Produtos | 20 | 3 |
| Carrinho | 15 | 2 |
| **Total** | **63** | **5** |

---

## 🔍 Boas Práticas Aplicadas

✅ Fixtures com `yield` e teardown automático
✅ Dados dinâmicos com UUID — zero hardcode
✅ Separação de responsabilidades (helpers / generators / fixtures)
✅ Testes independentes — executáveis em qualquer ordem
✅ Padrão AAA (Arrange, Act, Assert)
✅ JSON Schema em todos os endpoints de listagem e busca
✅ Testes exploratórios documentados como regressão de bugs
✅ CI/CD com GitHub Actions (main, develop, feature/**)
✅ `pytest-timeout` para proteção contra travamentos de rede
✅ Cobertura 100% das operações mapeadas
✅ Estratégia de branches (main → develop → feature)
