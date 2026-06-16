# 🚀 ServeRest API Test Automation

Projeto de automação de testes de API desenvolvido com Python, Pytest e Requests para validação dos principais fluxos da API ServeRest.

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

https://compassuol.serverest.dev/

---

## 🛠️ Stack

| Ferramenta | Versão | Finalidade |
|---|---|---|
| Python | 3.10+ | Linguagem base |
| Pytest | 7.4.3 | Framework de testes |
| Requests | 2.31.0 | Chamadas HTTP |
| jsonschema | 4.23.0 | Validação de estrutura JSON |
| pytest-html | 4.1.1 | Relatório HTML |
| GitHub Actions | — | CI/CD automático |

---

## 📂 Estrutura do Projeto

```text
desafio01-bootcamp-qa/
│
├── .github/
│   └── workflows/
│       └── tests.yml          ← GitHub Actions CI
│
├── helpers/
│   ├── carrinho_helper.py
│   ├── generators.py
│   ├── login_helper.py
│   ├── produtos_helper.py
│   └── usuarios_helper.py
│
├── tests/
│   ├── test_carrinho.py       ← 14 testes
│   ├── test_login.py          ← 7 testes
│   ├── test_produtos.py       ← 20 testes
│   └── test_usuarios.py       ← 20 testes
│
├── conftest.py
├── PLANO-DE-TESTES.md
├── pytest.ini
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
| `usuario_criado` | function | Cria usuário admin + teardown automático |
| `token_admin` | function | Token JWT de administrador |
| `usuario_nao_admin` | function | Cria usuário comum + teardown |
| `token_nao_admin` | function | Token JWT de não-administrador |
| `produto_criado` | function | Cria produto + teardown automático |

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
pytest                                          # suíte completa
pytest -v                                       # modo detalhado
pytest tests/test_login.py -v                  # só login
pytest tests/test_produtos.py -v               # só produtos
pytest tests/test_usuarios.py -v               # só usuários
pytest tests/test_carrinho.py -v               # só carrinho
pytest --html=report.html --self-contained-html # com relatório HTML
pytest -k "BUG" -v                             # só testes de bug
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
| Bugs documentados | 5 |

Nenhuma operação ficou fora da cobertura nesta versão.

---

## 🐛 Bugs Encontrados e Reportados

Os bugs abaixo foram descobertos durante a execução exploratória da suíte e estão
documentados como Issues no repositório. Cada bug tem um teste de regressão correspondente.

### BUG #1 — Contrato de erro inconsistente (`message` vs chave do campo)

**Severidade:** Média  
**Endpoints afetados:** `POST /login`, `POST /usuarios`, `GET /usuarios/{id}`, `GET /produtos/{id}`

A maioria dos erros da API retorna `{"message": "..."}`. Porém, erros de validação
de campos individuais retornam a chave do campo como chave do JSON, por exemplo:
`{"email": "email não pode ficar em branco"}` ou `{"id": "id deve ter exatamente..."}`.
Isso quebra a consistência do contrato e força clientes a tratar dois formatos distintos.

**Evidência:**
```json
// Comportamento esperado (padrão da API)
{"message": "email não pode ficar em branco"}

// Comportamento obtido (inconsistente)
{"email": "email não pode ficar em branco"}
```

**Testes de regressão:** `test_login_sem_email_retorna_400`, `test_login_sem_password_retorna_400`,
`test_buscar_usuario_por_id_formato_invalido_retorna_400`, `test_buscar_produto_por_id_formato_invalido_retorna_400`

---

### BUG #2 — Senhas retornadas em texto puro (CRÍTICO)

**Severidade:** Crítica  
**Endpoints afetados:** `GET /usuarios`, `GET /usuarios/{id}`

O campo `password` é retornado com o valor em texto puro (plaintext) em todas as
respostas de listagem e busca de usuários. Senhas jamais deveriam ser retornadas em
respostas de API — deveriam ser omitidas ou armazenadas/exibidas apenas como hash.
Esta vulnerabilidade expõe credenciais de todos os usuários para qualquer pessoa
com acesso à API, sem necessidade de autenticação.

**Evidência:**
```json
// GET /usuarios/{id}
{
  "nome": "QA Bug Hunter",
  "email": "qa_abc123@serverest.dev",
  "password": "minha_senha_secreta_123",   // ← EXPOSTA EM PLAINTEXT
  "administrador": "true",
  "_id": "fGu1Uld3sdFVHUNZ"
}
```

**Testes de regressão:** `test_senha_exposta_em_texto_puro_no_get_por_id`,
`test_senha_exposta_em_listagem_de_usuarios`

---

### BUG #3 — Produto com `quantidade=0` aceito no cadastro mas inutilizável

**Severidade:** Média  
**Endpoint afetado:** `POST /produtos`

A API aceita o cadastro de produtos com `quantidade: 0` (retorna 201), porém ao
tentar adicionar esse produto a um carrinho, o sistema retorna 400 por "estoque
insuficiente". O produto fica permanentemente inutilizável no fluxo de compra sem
qualquer aviso ao momento do cadastro. O comportamento esperado seria rejeitar o
cadastro com `quantidade=0` ou ao menos retornar um aviso.

**Evidência:**
```
POST /produtos  {"quantidade": 0}  → 201 ✅ (aceito)
POST /carrinhos {"quantidade": 1}  → 400 ❌ "Produto não possui quantidade suficiente"
```

**Teste de regressão:** `test_criar_produto_quantidade_zero_aceito_mas_inutilizavel`

---

### BUG #4 — Campo `quantidade` aceita string numérica silenciosamente

**Severidade:** Baixa  
**Endpoint afetado:** `POST /produtos`

O campo `quantidade` da API é definido como inteiro, mas ao enviar o valor como
string JSON (`"10"` em vez de `10`), a API aceita e retorna 201 sem nenhuma
mensagem de aviso ou erro. A coerção silenciosa de tipos pode esconder erros
de integração em clientes que enviam os dados como strings.

**Evidência:**
```json
// Payload enviado (quantidade como string)
{"nome": "X", "preco": 10, "descricao": "x", "quantidade": "10"}

// Resposta (deveria ser 400, mas é 201)
{"message": "Cadastro realizado com sucesso", "_id": "b7wO9adF3ngF77J3"}
```

**Teste de regressão:** `test_criar_produto_quantidade_como_string_aceito`

---

### BUG #5 — `DELETE /concluir-compra` e `/cancelar-compra` retornam 200 para recurso inexistente

**Severidade:** Baixa  
**Endpoints afetados:** `DELETE /carrinhos/concluir-compra`, `DELETE /carrinhos/cancelar-compra`

Ao chamar os endpoints de finalização/cancelamento de compra sem ter um carrinho
ativo, a API retorna status 200 com a mensagem `"Não foi encontrado carrinho para
esse usuário"`. O correto semanticamente seria retornar 404 (Not Found), pois
o recurso solicitado não existe. O 200 pode levar clientes a interpretar que a
operação foi bem-sucedida.

**Evidência:**
```
DELETE /carrinhos/concluir-compra  (sem carrinho)
→ Status: 200
→ Body: {"message": "Não foi encontrado carrinho para esse usuário"}
```

**Testes de regressão:** `test_concluir_compra_sem_carrinho_retorna_200_com_aviso`,
`test_cancelar_compra_sem_carrinho_retorna_200_com_aviso`

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
| U01 | Listar → 200 + schema | ✅ |
| U02 | `quantidade` igual ao tamanho do array | ✅ |
| U03 | Filtro `?administrador=true` | ✅ |
| U04 | Filtro case-sensitive → 400 | ✅ |
| U05 | Cadastro válido → 201 | ✅ |
| U06 | E-mail duplicado → 400 | ✅ |
| U07–U09 | Campos obrigatórios ausentes → 400 | ✅ |
| U10 | Campo extra desconhecido → 400 | ✅ |
| U11 | `administrador` como booleano → 400 | ✅ |
| U12 | Senha exposta GET /{id} `[BUG #2]` | ✅ |
| U13 | Senha exposta na listagem `[BUG #2]` | ✅ |
| U14–U16 | Busca por ID (válido, inexistente, formato inválido) | ✅ |
| U17 | Atualizar existente → 200 | ✅ |
| U18 | Atualizar inexistente → 201 (upsert) | ✅ |
| U19 | Excluir existente → 200 | ✅ |
| U20 | Excluir inexistente → 200 | ✅ |

### 📦 Produtos (20 testes)

| ID | Cenário | Status |
|---|---|---|
| P01 | Listar → 200 + schema | ✅ |
| P02 | Filtro por nome | ✅ |
| P03 | Criar com token admin → 201 | ✅ |
| P04 | Criar sem token → 401 | ✅ |
| P05 | Criar com token não-admin → 403 | ✅ |
| P06 | Nome duplicado → 400 | ✅ |
| P07 | Token inválido → 401 | ✅ |
| P08 | Qtd=0 aceita, inutilizável no carrinho `[BUG #3]` | ✅ |
| P09 | Qtd como string aceita `[BUG #4]` | ✅ |
| P10 | Preço float → 400 | ✅ |
| P11 | Preço negativo → 400 | ✅ |
| P12 | Quantidade negativa → 400 | ✅ |
| P13 | Buscar válido → 200 + schema | ✅ |
| P14 | Buscar ID formato inválido → 400 `[BUG #1]` | ✅ |
| P15 | Buscar ID inexistente → 400 | ✅ |
| P16 | Atualizar existente → 200 | ✅ |
| P17 | Atualizar com nome duplicado → 400 | ✅ |
| P18 | Atualizar inexistente → 201 (upsert) | ✅ |
| P19 | Excluir sem carrinho → 200 | ✅ |
| P20 | Excluir com carrinho ativo → 400 | ✅ |

### 🛒 Carrinhos (14 testes)

| ID | Cenário | Status |
|---|---|---|
| C01 | Listar → 200 + schema | ✅ |
| C02 | Criar com produto válido → 201 | ✅ |
| C03 | Schema do carrinho criado | ✅ |
| C04 | Segundo carrinho mesmo usuário → 400 | ✅ |
| C05 | Produto inexistente → 400 | ✅ |
| C06 | Qtd acima do estoque → 400 + detalhe | ✅ |
| C07 | Produto duplicado no array → 400 | ✅ |
| C08 | Buscar por ID → 200 | ✅ |
| C09 | Buscar inexistente → 400 | ✅ |
| C10 | Cancelar com carrinho → 200 | ✅ |
| C11 | Concluir com carrinho → 200 | ✅ |
| C12 | Concluir sem carrinho → 200 `[BUG #5]` | ✅ |
| C13 | Cancelar sem carrinho → 200 `[BUG #5]` | ✅ |
| C14 | Cancelar restaura estoque | ✅ |

---

## 🔍 Extras Implementados

### Extra 1 — JSON Schema (5 endpoints)

| Arquivo | Schema(s) |
|---|---|
| `test_login.py` | `LOGIN_SUCESSO_SCHEMA` |
| `test_usuarios.py` | `USUARIO_SCHEMA`, `LISTA_USUARIOS_SCHEMA` |
| `test_produtos.py` | `PRODUTO_SCHEMA`, `LISTA_PRODUTOS_SCHEMA` |
| `test_carrinho.py` | `CARRINHO_SCHEMA`, `LISTA_CARRINHOS_SCHEMA` |

### Extra 2 — GitHub Actions

Pipeline em `.github/workflows/tests.yml`:
- Executa em todo push e pull request
- Publica relatório HTML como artefato

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
✅ CI/CD com GitHub Actions  
✅ Cobertura 100% das operações mapeadas  
