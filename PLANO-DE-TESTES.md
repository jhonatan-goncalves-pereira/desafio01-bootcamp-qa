# Plano de Testes — ServeRest API
---

## 1. Objetivo

Validar os principais fluxos funcionais da API ServeRest (`https://compassuol.serverest.dev`) por
meio de testes automatizados, garantindo que os endpoints respondam corretamente em cenários
positivos (happy path), negativos, de borda e exploratórios. Bugs encontrados durante a
execução são documentados como Issues no repositório e cobertos por testes de regressão.

---

## 2. Estratégia

| Dimensão | Decisão |
|---|---|
| Tipo de teste | Testes de API caixa-preta (funcional + exploratório) |
| Camada | Integração — chamadas HTTP reais contra o ambiente de homologação |
| Ferramentas | Python 3.10+, Pytest, Requests, jsonschema |
| Geração de dados | Dados dinâmicos via `generators.py` (UUID) para evitar colisões |
| Isolamento | Fixtures com `yield` + teardown automático por teste |
| Autenticação | Fixtures `token_admin` e `token_nao_admin` para cobrir ambos os perfis |
| Bugs | Descobertos via script exploratório; cobertos por testes de regressão marcados com `[BUG #N]` |
| Cobertura | Medida pela fórmula: `(operações testadas / total de operações mapeadas) × 100` |

---

## 3. Escopo

### ✅ Dentro do escopo

| Endpoint | Métodos cobertos |
|---|---|
| `/login` | POST |
| `/usuarios` | GET, POST, GET /{id}, PUT /{id}, DELETE /{id} |
| `/produtos` | GET, POST, GET /{id}, PUT /{id}, DELETE /{id} |
| `/carrinhos` | GET, POST, GET /{id}, DELETE /cancelar-compra, DELETE /concluir-compra |

### ❌ Fora do escopo (e por quê)

| Item | Motivo |
|---|---|
| Testes de performance/carga | Requer ferramentas dedicadas (k6, Locust) e autorização |
| Testes de segurança (injeção, XSS) | Requer abordagem especializada e escopo formal |
| Testes de contrato (Pact) | Fora do escopo do bootcamp |
| Paginação / ordenação | API não documenta suporte a paginação |

---

## 4. Cenários Implementados

### 🔐 POST /login

| ID | Cenário | Tipo |
|---|---|---|
| L01 | Credenciais válidas → 200 + token Bearer JWT | Positivo |
| L02 | Token retornado tem 3 partes (header.payload.signature) | Positivo |
| L03 | Senha incorreta → 401 | Negativo |
| L04 | E-mail inexistente → 401 | Negativo |
| L05 | Campo e-mail vazio → 400 `[BUG #1]` | Negativo |
| L06 | Campo password vazio → 400 `[BUG #1]` | Negativo |
| L07 | Ambos os campos vazios → 400 | Negativo |

### 👤 /usuarios

| ID | Cenário | Tipo |
|---|---|---|
| U01 | Listar usuários → 200 + schema válido | Positivo |
| U02 | Campo `quantidade` igual ao tamanho do array | Positivo |
| U03 | Filtro `?administrador=true` retorna só admins | Positivo |
| U04 | Filtro `?administrador=True` (maiúsculo) → 400 (case-sensitive) | Negativo |
| U05 | Cadastrar usuário válido → 201 com `_id` | Positivo |
| U06 | E-mail duplicado → 400 | Negativo |
| U07 | Sem nome → 400 | Negativo |
| U08 | Sem e-mail → 400 | Negativo |
| U09 | Sem password → 400 | Negativo |
| U10 | Campo extra desconhecido → 400 | Negativo |
| U11 | Campo `administrador` como booleano JSON → 400 | Negativo |
| U12 | GET /{id} expõe senha em texto puro `[BUG #2]` | Bug/Segurança |
| U13 | GET / listagem expõe senhas em texto puro `[BUG #2]` | Bug/Segurança |
| U14 | Buscar por ID válido → 200 + schema | Positivo |
| U15 | Buscar ID inexistente (16 chars) → 400 | Negativo |
| U16 | Buscar ID formato inválido (< 16 chars) → 400 `[BUG #1]` | Negativo |
| U17 | Atualizar existente → 200 | Positivo |
| U18 | Atualizar ID inexistente → 201 (upsert) | Borda |
| U19 | Excluir existente → 200 | Positivo |
| U20 | Excluir ID inexistente → 200 sem registro | Borda |

### 📦 /produtos

| ID | Cenário | Tipo |
|---|---|---|
| P01 | Listar produtos → 200 + schema | Positivo |
| P02 | Filtro `?nome=X` retorna produto correspondente | Positivo |
| P03 | Cadastrar com token admin → 201 | Positivo |
| P04 | Cadastrar sem token → 401 | Negativo |
| P05 | Cadastrar com token não-admin → 403 | Negativo |
| P06 | Nome duplicado → 400 | Negativo |
| P07 | Token completamente inválido → 401 | Negativo |
| P08 | Quantidade=0 aceita no cadastro, bloqueia no carrinho `[BUG #3]` | Bug/Borda |
| P09 | Quantidade como string aceita silenciosamente `[BUG #4]` | Bug/Borda |
| P10 | Preço float (10.99) → 400 | Negativo |
| P11 | Preço negativo → 400 | Negativo |
| P12 | Quantidade negativa → 400 | Negativo |
| P13 | Buscar por ID válido → 200 + schema | Positivo |
| P14 | Buscar ID formato inválido → 400 `[BUG #1]` | Negativo |
| P15 | Buscar ID inexistente (16 chars) → 400 | Negativo |
| P16 | Atualizar existente → 200 | Positivo |
| P17 | Atualizar com nome de outro produto → 400 | Negativo |
| P18 | Atualizar ID inexistente → 201 (upsert) | Borda |
| P19 | Excluir sem carrinho ativo → 200 | Positivo |
| P20 | Excluir com carrinho ativo → 400 | Negativo |

### 🛒 /carrinhos

| ID | Cenário | Tipo |
|---|---|---|
| C01 | Listar carrinhos → 200 + schema | Positivo |
| C02 | Criar com produto válido → 201 | Positivo |
| C03 | Schema do carrinho criado é válido | Positivo |
| C04 | Segundo carrinho mesmo usuário → 400 | Negativo |
| C05 | Produto inexistente → 400 | Negativo |
| C06 | Quantidade acima do estoque → 400 com detalhe do item | Negativo |
| C07 | Produto duplicado no array → 400 | Negativo |
| C08 | Buscar por ID → 200 | Positivo |
| C09 | Buscar ID inexistente → 400 | Negativo |
| C10 | Cancelar compra com carrinho → 200 | Positivo |
| C11 | Concluir compra com carrinho → 200 | Positivo |
| C12 | Concluir sem carrinho → 200 com aviso `[BUG #5]` | Bug/Borda |
| C13 | Cancelar sem carrinho → 200 com aviso `[BUG #5]` | Bug/Borda |
| C14 | Cancelar compra restaura estoque do produto | Regressão |

---

## 5. Bugs Encontrados

| # | Título | Severidade | Endpoint(s) | Issue |
|---|---|---|---|---|
| BUG #1 | Contrato de erro inconsistente — chave do campo em vez de `message` | Média | `/login`, `/usuarios`, `/produtos`, `/carrinhos` | #1 |
| BUG #2 | Senhas retornadas em texto puro (plaintext) nas respostas | **Crítica** | `GET /usuarios`, `GET /usuarios/{id}` | #2 |
| BUG #3 | Produto com `quantidade=0` aceito no cadastro mas inutilizável no carrinho | Média | `POST /produtos` | #3 |
| BUG #4 | Campo `quantidade` aceita string numérica em vez de rejeitar | Baixa | `POST /produtos` | #4 |
| BUG #5 | `DELETE /concluir-compra` e `/cancelar-compra` retornam 200 para recurso inexistente | Baixa | `DELETE /carrinhos/*` | #5 |

---

## 6. Critérios de Qualidade

Um teste é considerado **pronto** quando atende a todos os critérios abaixo:

- [x] **Isolado**: não depende de estado deixado por outro teste
- [x] **Determinístico**: passa ou falha de forma consistente em múltiplas execuções
- [x] **Sem dados fixos**: utiliza dados gerados dinamicamente (sem e-mails/IDs hardcoded)
- [x] **Teardown implementado**: recursos criados durante o teste são removidos ao final
- [x] **Assert significativo**: valida status code + pelo menos um campo do corpo
- [x] **Nomenclatura clara**: nome do teste descreve o cenário sem ambiguidade
- [x] **Bugs documentados**: testes de bug têm comentário `[BUG #N]` no docstring
- [x] **JSON Schema**: endpoints principais validam estrutura da resposta

---

## 7. Histórico de Atualizações

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-15 | 1.0 | Criação do plano inicial |
| 2026-06-15 | 1.1 | Expansão cobertura Login e Produtos |
| 2026-06-15 | 2.0 | Execução exploratória; 5 bugs identificados; 61 testes; cobertura 100% |
