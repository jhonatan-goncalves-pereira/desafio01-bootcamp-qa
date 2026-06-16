# 🚀 ServeRest API Test Automation

Projeto de automação de testes de API desenvolvido com Python, Pytest e Requests para
validação dos principais fluxos da API ServeRest.

> Desafio desenvolvido durante o Bootcamp QA da Compass UOL (AI/R Fellowship).

![Tests](https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa/actions/workflows/tests.yml/badge.svg)

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
main                    ← produção estável
└── develop             ← integração contínua
    └── feature/bug-report-e-melhorias  ← desenvolvimento atual
```

| Branch | Propósito |
|---|---|
| `main` | Código estável, entregável final |
| `develop` | Integração de features antes de ir para main |
| `feature/bug-report-e-melhorias` | Bug reports documentados + melhorias identificadas |

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
│   ├── test_carrinho.py       ← 14 testes
│   ├── test_login.py          ← 7 testes
│   ├── test_produtos.py       ← 20 testes
│   └── test_usuarios.py       ← 20 testes
│
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

### Método utilizado

Cobertura calculada conforme o artigo
[Como verificar a cobertura de testes da API REST](https://medium.com/revista-dtar/como-verificar-a-cobertura-de-testes-da-api-rest-9e2f745564b).
A métrica é baseada em **operações** — cada par `endpoint + método HTTP` é uma operação.

```
Cobertura (%) = (operações com pelo menos 1 teste / total de operações mapeadas) × 100
```

### Mapeamento das operações

| Endpoint | Método | Operação | Coberta? |
|---|---|---|---|
| `/login` | POST | Autenticar usuário | ✅ |
| `/usuarios` | GET | Listar usuários | ✅ |
| `/usuarios` | POST | Criar usuário | ✅ |
| `/usuarios/{id}` | GET | Buscar usuário por ID | ✅ |
| `/usuarios/{id}` | PUT | Atualizar usuário | ✅ |
| `/usuarios/{id}` | DELETE | Excluir usuário | ✅ |
| `/produtos` | GET | Listar produtos | ✅ |
| `/produtos` | POST | Criar produto | ✅ |
| `/produtos/{id}` | GET | Buscar produto por ID | ✅ |
| `/produtos/{id}` | PUT | Atualizar produto | ✅ |
| `/produtos/{id}` | DELETE | Excluir produto | ✅ |
| `/carrinhos` | GET | Listar carrinhos | ✅ |
| `/carrinhos` | POST | Criar carrinho | ✅ |
| `/carrinhos/{id}` | GET | Buscar carrinho por ID | ✅ |
| `/carrinhos/cancelar-compra` | DELETE | Cancelar compra | ✅ |
| `/carrinhos/concluir-compra` | DELETE | Concluir compra | ✅ |

### Resultado

| Métrica | Valor |
|---|---|
| Total de operações mapeadas | 16 |
| Operações cobertas | 16 |
| **Cobertura de operações** | **100%** |
| Total de testes automatizados | 61 |
| Testes passando | 61 |
| Bugs documentados e reportados | 5 |
| Melhorias identificadas | 7 |

---

## 🐛 Bugs Encontrados e Reportados

Os bugs abaixo foram descobertos durante a execução exploratória da suíte e estão
documentados como Issues no repositório. Cada bug tem um teste de regressão correspondente.

### BUG #1 — Contrato de erro inconsistente (`message` vs chave do campo)

**Severidade:** Média
**Endpoints afetados:** `POST /login`, `POST /usuarios`, `GET /usuarios/{id}`, `GET /produtos/{id}`

A maioria dos erros da API retorna `{"message": "..."}`. Porém, erros de validação de
campos individuais retornam a chave do campo como chave do JSON — por exemplo:
`{"email": "email não pode ficar em branco"}` em vez de `{"message": "..."}`.
Isso força clientes a tratar dois formatos distintos de erro.

```json
// Esperado (padrão da API)
{"message": "email não pode ficar em branco"}

// Obtido (inconsistente)
{"email": "email não pode ficar em branco"}
```

**Testes de regressão:** `test_login_sem_email_retorna_400`, `test_login_sem_password_retorna_400`,
`test_buscar_usuario_por_id_formato_invalido_retorna_400`, `test_buscar_produto_por_id_formato_invalido_retorna_400`

---

### BUG #2 — Senhas retornadas em texto puro (CRÍTICO)

**Severidade:** Crítica
**Endpoints afetados:** `GET /usuarios`, `GET /usuarios/{id}`

O campo `password` é retornado em plaintext em todas as respostas de listagem e busca
de usuários, sem necessidade de autenticação. Senhas deveriam ser omitidas ou exibidas
apenas como hash.

```json
{
  "nome": "QA Bug Hunter",
  "email": "qa_abc123@qa.com",
  "password": "minha_senha_secreta_123",
  "administrador": "true",
  "_id": "fGu1Uld3sdFVHUNZ"
}
```

**Testes de regressão:** `test_senha_exposta_em_texto_puro_no_get_por_id`,
`test_senha_exposta_em_listagem_de_usuarios`

---

### BUG #3 — Produto com `quantidade=0` aceito mas inutilizável no carrinho

**Severidade:** Média
**Endpoint afetado:** `POST /produtos`

A API aceita cadastro de produtos com `quantidade: 0` (retorna 201), mas ao tentar
adicionar ao carrinho retorna 400 por "estoque insuficiente". O produto fica
permanentemente inutilizável no fluxo de compra.

```
POST /produtos  {"quantidade": 0}  → 201 ✅ (aceito)
POST /carrinhos {"quantidade": 1}  → 400 ❌ "Produto não possui quantidade suficiente"
```

**Teste de regressão:** `test_criar_produto_quantidade_zero_aceito_mas_inutilizavel`

---

### BUG #4 — Campo `quantidade` aceita string numérica silenciosamente

**Severidade:** Baixa
**Endpoint afetado:** `POST /produtos`

O campo `quantidade` aceita strings JSON (`"10"`) quando deveria exigir inteiro.
A coerção silenciosa pode esconder erros de integração.

```json
// Enviado
{"nome": "X", "preco": 10, "descricao": "x", "quantidade": "10"}

// Resposta (deveria ser 400)
{"message": "Cadastro realizado com sucesso", "_id": "b7wO9adF3ngF77J3"}
```

**Teste de regressão:** `test_criar_produto_quantidade_como_string_aceito`

---

### BUG #5 — DELETE sem carrinho ativo retorna 200 em vez de 404

**Severidade:** Baixa
**Endpoints afetados:** `DELETE /carrinhos/concluir-compra`, `DELETE /carrinhos/cancelar-compra`

Sem carrinho ativo, a API retorna 200 com mensagem de aviso. Semanticamente, o correto
seria 404 (Not Found) pois o recurso solicitado não existe.

```
DELETE /carrinhos/concluir-compra  (sem carrinho ativo)
→ Status: 200
→ Body: {"message": "Não foi encontrado carrinho para esse usuário"}
```

**Testes de regressão:** `test_concluir_compra_sem_carrinho_retorna_200_com_aviso`,
`test_cancelar_compra_sem_carrinho_retorna_200_com_aviso`

---

## 💡 Melhorias Identificadas

Além dos bugs funcionais, foram mapeadas oportunidades de evolução da suíte:

| # | Descrição | Área | Prioridade |
|---|---|---|---|
| M01 | Validar comportamento de `preco=0` no cadastro de produto | Produtos | Média |
| M02 | Testar criação de carrinho sem token (401 esperado) | Carrinhos | Média |
| M03 | Verificar filtro `GET /carrinhos?idUsuario=X` | Carrinhos | Baixa |
| M04 | Testar comportamento com token expirado (após 600s) | Auth | Alta |
| M05 | Validar bloqueio de exclusão de usuário com carrinho ativo | Usuários | Alta |
| M06 | Testar campos em branco (`""`) vs. campo ausente (comportamento diferente?) | Geral | Média |
| M07 | Parametrizar testes de campos obrigatórios com `@pytest.mark.parametrize` | Refactor | Baixa |

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

### 👤 Usuários (20 testes)

| ID | Cenário | Status |
|---|---|---|
| U01–U02 | Listar → 200 + schema + `quantidade` correto | ✅ |
| U03–U04 | Filtros por `administrador` (true / case-sensitive) | ✅ |
| U05–U11 | Cadastro (válido, duplicado, campos ausentes, tipo errado) | ✅ |
| U12–U13 | Senha exposta em plaintext `[BUG #2]` | ✅ |
| U14–U16 | Busca por ID (válido, inexistente, formato inválido) | ✅ |
| U17–U18 | Atualizar (existente, upsert) | ✅ |
| U19–U20 | Excluir (existente, inexistente) | ✅ |

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

### 🛒 Carrinhos (14 testes)

| ID | Cenário | Status |
|---|---|---|
| C01–C03 | Listar + criar + validar schema | ✅ |
| C04–C07 | Restrições (2 carrinhos, produto inexistente, estoque, duplicado) | ✅ |
| C08–C09 | Buscar (existente, inexistente) | ✅ |
| C10–C11 | Cancelar e concluir com carrinho | ✅ |
| C12–C13 | Cancelar/concluir sem carrinho `[BUG #5]` | ✅ |
| C14 | Cancelar restaura estoque | ✅ |

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
| Usuários | 20 | 2 |
| Produtos | 20 | 3 |
| Carrinho | 14 | 2 |
| **Total** | **61** | **5** |

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
