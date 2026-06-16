# 🐛 Bug Reports — ServeRest API

> Bugs encontrados durante a execução exploratória da suíte automatizada.
> Cada bug está reportado também como **Issue no GitHub** com evidências e testes de regressão.
>
> **API:** https://compassuol.serverest.dev
> **Projeto:** Desafio 01 — Bootcamp QA AI/R (Compass UOL)

---

## BUG #1 — Contrato de erro inconsistente

| Campo | Detalhe |
|---|---|
| **Título** | Erros de validação retornam chave do campo em vez de `message` |
| **Severidade** | 🟡 Média |
| **Prioridade** | P2 |
| **Tipo** | Contrato de API / Inconsistência |
| **Endpoints** | `POST /login`, `POST /usuarios`, `GET /usuarios/{id}`, `GET /produtos/{id}` |
| **Issue GitHub** | #1 |

### Descrição

A API retorna erros de validação em dois formatos distintos. Na maioria dos casos
o padrão é `{"message": "..."}`, mas em erros de campo específico a chave do JSON
é o nome do campo — por exemplo `{"email": "..."}` ou `{"id": "..."}`.
Isso força clientes a implementar dois parsers diferentes para erros.

### Passos para Reproduzir

```bash
# Passo 1: Login sem e-mail
POST /login
Body: {"email": "", "password": "teste"}

# Passo 2: Buscar usuário com ID curto
GET /usuarios/abc
```

### Comportamento Esperado

```json
{"message": "email não pode ficar em branco"}
{"message": "id deve ter exatamente 16 caracteres"}
```

### Comportamento Obtido

```json
{"email": "email não pode ficar em branco"}
{"id": "id deve ter exatamente 16 caracteres"}
```

### Testes de Regressão

- `test_login_sem_email_retorna_400`
- `test_login_sem_password_retorna_400`
- `test_buscar_usuario_por_id_formato_invalido_retorna_400`
- `test_buscar_produto_por_id_formato_invalido_retorna_400`

---

## BUG #2 — Senhas retornadas em texto puro (CRÍTICO)

| Campo | Detalhe |
|---|---|
| **Título** | `GET /usuarios` e `GET /usuarios/{id}` expõem senhas em plaintext |
| **Severidade** | 🔴 Crítica |
| **Prioridade** | P0 |
| **Tipo** | Segurança / Exposição de dados sensíveis |
| **Endpoints** | `GET /usuarios`, `GET /usuarios/{id}` |
| **Issue GitHub** | #2 |

### Descrição

O campo `password` é retornado com o valor em texto puro em todas as respostas de
listagem e busca de usuários. Qualquer pessoa com acesso à API pode obter as senhas
de todos os usuários cadastrados sem autenticação — a listagem é pública.

Senhas **jamais** devem ser retornadas em respostas de API. Deveriam ser omitidas
ou armazenadas/retornadas apenas como hash irreversível (bcrypt, argon2, etc).

### Passos para Reproduzir

```bash
# Qualquer um pode executar sem token:
GET /usuarios
GET /usuarios/{qualquer_id_valido}
```

### Comportamento Esperado

```json
{
  "nome": "Fulano da Silva",
  "email": "fulano@qa.com",
  "administrador": "true",
  "_id": "abc123"
  // campo password AUSENTE ou como hash
}
```

### Comportamento Obtido

```json
{
  "nome": "Fulano da Silva",
  "email": "fulano@qa.com",
  "password": "teste",
  "administrador": "true",
  "_id": "abc123"
}
```

### Impacto

- Exposição de credenciais de todos os usuários sem autenticação
- Reutilização de senha em outros serviços (credential stuffing)
- Violação de LGPD/GDPR — dado pessoal sensível exposto

### Testes de Regressão

- `test_senha_exposta_em_texto_puro_no_get_por_id`
- `test_senha_exposta_em_listagem_de_usuarios`

---

## BUG #3 — Produto com `quantidade=0` aceito mas inutilizável

| Campo | Detalhe |
|---|---|
| **Título** | `POST /produtos` aceita `quantidade=0` mas impede uso no carrinho |
| **Severidade** | 🟡 Média |
| **Prioridade** | P2 |
| **Tipo** | Validação de entrada / Inconsistência de regra de negócio |
| **Endpoint** | `POST /produtos` |
| **Issue GitHub** | #3 |

### Descrição

A API aceita o cadastro de produtos com `quantidade: 0` retornando status 201.
Porém, ao tentar adicionar esse produto a um carrinho, o sistema retorna 400
por "estoque insuficiente". O produto fica permanentemente inutilizável no
fluxo de compra sem qualquer aviso no momento do cadastro.

### Passos para Reproduzir

```bash
# Passo 1: Criar produto com quantidade zero
POST /produtos
Headers: Authorization: Bearer <token_admin>
Body: {"nome": "Prod Zero", "preco": 10, "descricao": "test", "quantidade": 0}
→ 201 ✅

# Passo 2: Tentar adicionar ao carrinho
POST /carrinhos
Body: {"produtos": [{"idProduto": "<id>", "quantidade": 1}]}
→ 400 ❌ "Produto não possui quantidade suficiente para a quantidade solicitada"
```

### Comportamento Esperado

`POST /produtos` com `quantidade: 0` deveria retornar **400** com mensagem explicativa,
ou ao menos um aviso (ex: `"warning": "produto sem estoque inicial"`).

### Comportamento Obtido

`POST /produtos` retorna **201** e o produto é criado. Qualquer tentativa posterior
de uso no carrinho falha com 400.

### Teste de Regressão

- `test_criar_produto_quantidade_zero_aceito_mas_inutilizavel`

---

## BUG #4 — Campo `quantidade` aceita string numérica silenciosamente

| Campo | Detalhe |
|---|---|
| **Título** | `POST /produtos` aceita `"quantidade": "10"` (string) sem erro |
| **Severidade** | 🟢 Baixa |
| **Prioridade** | P3 |
| **Tipo** | Validação de tipo / Coerção silenciosa |
| **Endpoint** | `POST /produtos` |
| **Issue GitHub** | #4 |

### Descrição

O campo `quantidade` é definido como inteiro no contrato da API, mas ao enviar
o valor como string JSON (`"10"` em vez de `10`), a API aceita e retorna 201
sem nenhuma mensagem de aviso ou erro. A coerção silenciosa de tipos pode
esconder erros de integração em clientes que trafegam dados via formulários
HTML (onde todos os valores chegam como string).

### Passos para Reproduzir

```bash
POST /produtos
Headers: Authorization: Bearer <token_admin>
Body: {
  "nome": "Produto String Qty",
  "preco": 10,
  "descricao": "teste",
  "quantidade": "10"   ← string, não inteiro
}
→ 201 (deveria ser 400)
```

### Comportamento Esperado

```json
// 400 Bad Request
{"quantidade": "quantidade deve ser um número inteiro"}
```

### Comportamento Obtido

```json
// 201 Created
{"message": "Cadastro realizado com sucesso", "_id": "xxx"}
```

### Teste de Regressão

- `test_criar_produto_quantidade_como_string_aceito`

---

## BUG #5 — DELETE sem carrinho ativo retorna 200 em vez de 404

| Campo | Detalhe |
|---|---|
| **Título** | `DELETE /concluir-compra` e `/cancelar-compra` retornam 200 para recurso inexistente |
| **Severidade** | 🟢 Baixa |
| **Prioridade** | P3 |
| **Tipo** | Semântica HTTP / Status code incorreto |
| **Endpoints** | `DELETE /carrinhos/concluir-compra`, `DELETE /carrinhos/cancelar-compra` |
| **Issue GitHub** | #5 |

### Descrição

Ao chamar os endpoints de finalização ou cancelamento de compra sem ter um carrinho
ativo, a API retorna status **200** com mensagem `"Não foi encontrado carrinho para
esse usuário"`. O semanticamente correto seria **404** (Not Found), pois o recurso
solicitado não existe. O status 200 pode levar clientes a interpretar que a operação
foi bem-sucedida, silenciando um estado de erro.

### Passos para Reproduzir

```bash
# Sem nenhum carrinho ativo para o usuário:

DELETE /carrinhos/concluir-compra
Headers: Authorization: Bearer <token_valido>
→ Status: 200 ❌ (esperado: 404)

DELETE /carrinhos/cancelar-compra
Headers: Authorization: Bearer <token_valido>
→ Status: 200 ❌ (esperado: 404)
```

### Comportamento Esperado

```json
// 404 Not Found
{"message": "Não foi encontrado carrinho para esse usuário"}
```

### Comportamento Obtido

```json
// 200 OK ← semânticamente incorreto
{"message": "Não foi encontrado carrinho para esse usuário"}
```

### Testes de Regressão

- `test_concluir_compra_sem_carrinho_retorna_200_com_aviso`
- `test_cancelar_compra_sem_carrinho_retorna_200_com_aviso`

---

## 📋 Resumo dos Bugs

| # | Título resumido | Severidade | Prioridade | Issue |
|---|---|---|---|---|
| BUG #1 | Contrato de erro inconsistente | 🟡 Média | P2 | #1 |
| BUG #2 | Senhas em plaintext | 🔴 Crítica | P0 | #2 |
| BUG #3 | `quantidade=0` aceita, inutilizável | 🟡 Média | P2 | #3 |
| BUG #4 | `quantidade` aceita string | 🟢 Baixa | P3 | #4 |
| BUG #5 | DELETE sem carrinho retorna 200 | 🟢 Baixa | P3 | #5 |
