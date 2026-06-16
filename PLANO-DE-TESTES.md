# Plano de Testes — ServeRest API

> **Versão:** 2.1 | **Projeto:** Desafio 01 — Bootcamp QA AI/R (Compass UOL)
> **API:** https://compassuol.serverest.dev | **Última atualização:** 2026-06-16

---

## 1. Objetivo

Validar os principais fluxos funcionais da API ServeRest por meio de testes automatizados,
garantindo que os endpoints respondam corretamente em cenários positivos (happy path),
negativos, de borda e exploratórios.

Bugs encontrados durante a execução são documentados como Issues no repositório GitHub
e cobertos por testes de regressão identificados com a tag `[BUG #N]`.

---

## 2. Estratégia

| Dimensão | Decisão |
|---|---|
| Tipo de teste | Testes de API caixa-preta (funcional + exploratório) |
| Camada | Integração — chamadas HTTP reais contra o ambiente de homologação |
| Ferramentas | Python 3.10+, Pytest, Requests, jsonschema, pytest-timeout |
| Geração de dados | Dados dinâmicos via `generators.py` (UUID) para evitar colisões |
| Isolamento | Fixtures com `yield` + teardown automático por teste |
| Autenticação | Fixtures `token_admin` e `token_nao_admin` para cobrir ambos os perfis |
| Timeout | `pytest-timeout` com limite de 60s por teste para lidar com instabilidade do servidor |
| Bugs | Descobertos via execução exploratória; cobertos por testes de regressão `[BUG #N]` |
| Cobertura | Medida pela fórmula: `(operações testadas / total de operações mapeadas) × 100` |
| CI/CD | GitHub Actions — executa em push/PR para `main`, `develop` e `feature/**` |

---

## 3. Escopo

### ✅ Dentro do escopo

| Endpoint | Métodos cobertos |
|---|---|
| `/login` | POST |
| `/usuarios` | GET, POST, GET `/{id}`, PUT `/{id}`, DELETE `/{id}` |
| `/produtos` | GET, POST, GET `/{id}`, PUT `/{id}`, DELETE `/{id}` |
| `/carrinhos` | GET, POST, GET `/{id}`, DELETE `/cancelar-compra`, DELETE `/concluir-compra` |

### ❌ Fora do escopo (e por quê)

| Item | Motivo |
|---|---|
| Testes de performance/carga | Requer ferramentas dedicadas (k6, Locust) e autorização do mantenedor |
| Testes de segurança (injeção, XSS) | Requer abordagem especializada e escopo formal |
| Testes de contrato (Pact) | Fora do escopo do bootcamp |
| Paginação / ordenação | API não documenta suporte a paginação |

---

## 4. Cenários Implementados

### 🔐 POST /login — 7 testes

| ID | Cenário | Tipo | Status |
|---|---|---|---|
| L01 | Credenciais válidas → 200 + token Bearer JWT | Positivo | ✅ |
| L02 | Token retornado tem 3 partes (header.payload.signature) | Positivo | ✅ |
| L03 | Senha incorreta → 401 | Negativo | ✅ |
| L04 | E-mail inexistente → 401 | Negativo | ✅ |
| L05 | Campo e-mail vazio → 400 `[BUG #1]` | Negativo | ✅ |
| L06 | Campo password vazio → 400 `[BUG #1]` | Negativo | ✅ |
| L07 | Ambos os campos vazios → 400 | Negativo | ✅ |

### 👤 /usuarios — 20 testes

| ID | Cenário | Tipo | Status |
|---|---|---|---|
| U01 | Listar → 200 + JSON Schema válido | Positivo | ✅ |
| U02 | Campo `quantidade` igual ao tamanho do array | Positivo | ✅ |
| U03 | Filtro `?administrador=true` retorna só admins | Positivo | ✅ |
| U04 | Filtro `?administrador=True` (maiúsculo) → 400 | Negativo | ✅ |
| U05 | Cadastrar usuário válido → 201 com `_id` | Positivo | ✅ |
| U06 | E-mail duplicado → 400 | Negativo | ✅ |
| U07 | Sem campo `nome` → 400 | Negativo | ✅ |
| U08 | Sem campo `email` → 400 | Negativo | ✅ |
| U09 | Sem campo `password` → 400 | Negativo | ✅ |
| U10 | Campo extra desconhecido → 400 | Negativo | ✅ |
| U11 | `administrador` como booleano JSON → 400 | Negativo | ✅ |
| U12 | GET `/{id}` expõe senha em plaintext `[BUG #2]` | Bug / Segurança | ✅ |
| U13 | GET `/` expõe senhas em plaintext na listagem `[BUG #2]` | Bug / Segurança | ✅ |
| U14 | Buscar por ID válido → 200 + JSON Schema | Positivo | ✅ |
| U15 | Buscar ID inexistente (16 chars) → 400 | Negativo | ✅ |
| U16 | Buscar ID formato inválido (< 16 chars) → 400 `[BUG #1]` | Negativo | ✅ |
| U17 | Atualizar existente → 200 | Positivo | ✅ |
| U18 | Atualizar ID inexistente → 201 (upsert) | Borda | ✅ |
| U19 | Excluir existente → 200 | Positivo | ✅ |
| U20 | Excluir ID inexistente → 200 sem registro | Borda | ✅ |

### 📦 /produtos — 20 testes

| ID | Cenário | Tipo | Status |
|---|---|---|---|
| P01 | Listar → 200 + JSON Schema | Positivo | ✅ |
| P02 | Filtro `?nome=X` retorna produto correspondente | Positivo | ✅ |
| P03 | Criar com token admin → 201 | Positivo | ✅ |
| P04 | Criar sem token → 401 | Negativo | ✅ |
| P05 | Criar com token não-admin → 403 | Negativo | ✅ |
| P06 | Nome duplicado → 400 | Negativo | ✅ |
| P07 | Token completamente inválido → 401 | Negativo | ✅ |
| P08 | `quantidade=0` aceita no cadastro, bloqueia no carrinho `[BUG #3]` | Bug / Borda | ✅ |
| P09 | `quantidade` como string aceita silenciosamente `[BUG #4]` | Bug / Borda | ✅ |
| P10 | Preço float (10.99) → 400 | Negativo | ✅ |
| P11 | Preço negativo → 400 | Negativo | ✅ |
| P12 | Quantidade negativa → 400 | Negativo | ✅ |
| P13 | Buscar por ID válido → 200 + JSON Schema | Positivo | ✅ |
| P14 | Buscar ID formato inválido → 400 `[BUG #1]` | Negativo | ✅ |
| P15 | Buscar ID inexistente (16 chars) → 400 | Negativo | ✅ |
| P16 | Atualizar existente → 200 | Positivo | ✅ |
| P17 | Atualizar com nome de outro produto → 400 | Negativo | ✅ |
| P18 | Atualizar ID inexistente → 201 (upsert) | Borda | ✅ |
| P19 | Excluir sem carrinho ativo → 200 | Positivo | ✅ |
| P20 | Excluir com carrinho ativo → 400 | Negativo | ✅ |

### 🛒 /carrinhos — 14 testes

| ID | Cenário | Tipo | Status |
|---|---|---|---|
| C01 | Listar → 200 + JSON Schema | Positivo | ✅ |
| C02 | Criar com produto válido → 201 | Positivo | ✅ |
| C03 | Schema do carrinho criado é válido | Positivo | ✅ |
| C04 | Segundo carrinho mesmo usuário → 400 | Negativo | ✅ |
| C05 | Produto inexistente → 400 | Negativo | ✅ |
| C06 | Quantidade acima do estoque → 400 com detalhe do item | Negativo | ✅ |
| C07 | Produto duplicado no array → 400 | Negativo | ✅ |
| C08 | Buscar por ID → 200 | Positivo | ✅ |
| C09 | Buscar ID inexistente → 400 | Negativo | ✅ |
| C10 | Cancelar compra com carrinho → 200 | Positivo | ✅ |
| C11 | Concluir compra com carrinho → 200 | Positivo | ✅ |
| C12 | Concluir sem carrinho → 200 com aviso `[BUG #5]` | Bug / Borda | ✅ |
| C13 | Cancelar sem carrinho → 200 com aviso `[BUG #5]` | Bug / Borda | ✅ |
| C14 | Cancelar compra restaura estoque do produto | Regressão | ✅ |

---

## 5. Bugs Encontrados

Todos os bugs abaixo foram reportados como Issues no GitHub com passos de reprodução,
comportamento esperado vs. obtido, severidade e evidências.

| # | Título | Severidade | Endpoint(s) |
|---|---|---|---|
| BUG #1 | Contrato de erro inconsistente — chave do campo em vez de `message` | Média | `/login`, `/usuarios`, `/produtos` |
| BUG #2 | Senhas retornadas em texto puro nas respostas | **Crítica** | `GET /usuarios`, `GET /usuarios/{id}` |
| BUG #3 | Produto com `quantidade=0` aceito no cadastro mas inutilizável no carrinho | Média | `POST /produtos` |
| BUG #4 | Campo `quantidade` aceita string numérica silenciosamente | Baixa | `POST /produtos` |
| BUG #5 | `DELETE /concluir-compra` e `/cancelar-compra` retornam 200 para recurso inexistente | Baixa | `DELETE /carrinhos/*` |

---

## 6. Melhorias Identificadas

Durante a análise da suíte e da API, foram identificadas oportunidades de melhoria
que vão além dos bugs funcionais:

| # | Descrição | Área | Prioridade |
|---|---|---|---|
| M01 | Adicionar validação de campo `preco=0` — produto gratuito pode ser inconsistente | Produtos | Média |
| M02 | Testar criação de carrinho sem token (401 esperado) | Carrinhos | Média |
| M03 | Verificar comportamento de `GET /carrinhos` com filtro por `idUsuario` | Carrinhos | Baixa |
| M04 | Adicionar teste de token expirado (após 600s) — comportamento de renovação | Auth | Alta |
| M05 | Validar que `DELETE /usuarios/{id}` bloqueia exclusão de usuário com carrinho ativo | Usuários | Alta |
| M06 | Testar payload com campos em branco (`""`) vs. campo ausente — comportamento diferente? | Geral | Média |
| M07 | Parametrizar testes de validação de campos obrigatórios com `@pytest.mark.parametrize` | Refactor | Baixa |

---

## 7. Critérios de Qualidade

Um teste é considerado **pronto** quando atende a todos os critérios abaixo:

- [x] **Isolado** — não depende de estado deixado por outro teste
- [x] **Determinístico** — passa ou falha de forma consistente em múltiplas execuções
- [x] **Sem dados fixos** — usa dados gerados dinamicamente (sem e-mails/IDs hardcoded)
- [x] **Teardown implementado** — recursos criados durante o teste são removidos ao final
- [x] **Assert significativo** — valida status code + pelo menos um campo do corpo
- [x] **Nomenclatura clara** — nome do teste descreve o cenário sem ambiguidade
- [x] **Bugs documentados** — testes de regressão têm `[BUG #N]` no docstring
- [x] **JSON Schema** — endpoints principais validam estrutura da resposta

---

## 8. Histórico de Atualizações

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-15 | 1.0 | Criação do plano inicial com escopo e estratégia |
| 2026-06-15 | 1.1 | Expansão para Login e Produtos |
| 2026-06-15 | 2.0 | Execução exploratória — 5 bugs identificados; 61 testes; cobertura 100% |
| 2026-06-16 | 2.1 | Adição da seção de Melhorias Identificadas (M01–M07); histórico revisado |
