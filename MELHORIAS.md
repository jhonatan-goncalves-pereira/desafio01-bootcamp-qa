# 💡 Melhorias Identificadas — ServeRest API Test Suite

> Oportunidades de evolução da suíte de testes identificadas após a análise completa
> da cobertura e dos bugs encontrados na API ServeRest.
>
> **Projeto:** Desafio 01 — Bootcamp QA AI/R (Compass UOL)
> **Versão da suíte:** 2.1 | **Data:** 2026-06-16

---

## Como usar este documento

Cada melhoria tem:
- **Código** — identificador único (M01–M07)
- **Área** — módulo ou camada afetada
- **Prioridade** — Alta / Média / Baixa (impacto na cobertura e qualidade)
- **Esforço estimado** — em pontos de história (1=trivial, 3=médio, 5=complexo)
- **Descrição** — o que deve ser feito e por quê
- **Exemplo de implementação** — código ou pseudocódigo orientativo

---

## M01 — Validar comportamento de `preco=0` no cadastro de produto

| Campo | Detalhe |
|---|---|
| **Área** | Produtos |
| **Prioridade** | 🟡 Média |
| **Esforço** | 1 ponto |

### Descrição

O BUG #3 mostrou que `quantidade=0` é aceito silenciosamente. Existe a mesma
suspeita para `preco=0` — um produto "gratuito" pode ser inconsistente com
as regras de negócio de uma loja virtual. Este teste verificaria se a API
aceita, rejeita ou silencia esse valor.

### Exemplo

```python
def test_criar_produto_preco_zero(base_url, token_admin):
    """M01 — Verificar comportamento de preco=0 no cadastro."""
    payload = {**gerar_produto(), "preco": 0}
    response = criar_produto(base_url, token_admin, payload)
    # Documentar comportamento real: 201 (aceito) ou 400 (rejeitado)?
    assert response.status_code in (201, 400), (
        f"Comportamento inesperado: {response.status_code}"
    )
```

---

## M02 — Testar criação de carrinho sem token de autenticação

| Campo | Detalhe |
|---|---|
| **Área** | Carrinhos |
| **Prioridade** | 🟡 Média |
| **Esforço** | 1 ponto |

### Descrição

O endpoint `POST /carrinhos` exige autenticação, mas a suite atual não possui
um teste explícito para a tentativa sem token. Esse cenário valida que a
proteção de autenticação está ativa no endpoint de carrinho, assim como já
existe para `POST /produtos`.

### Exemplo

```python
def test_criar_carrinho_sem_token_retorna_401(base_url, produto_criado):
    """M02 — POST /carrinhos sem token deve retornar 401."""
    import requests as req
    response = req.post(
        f"{base_url}/carrinhos",
        json={"produtos": [{"idProduto": produto_criado["id"], "quantidade": 1}]},
    )
    assert response.status_code == 401
    assert "message" in response.json()
```

---

## M03 — Verificar filtro `GET /carrinhos?idUsuario=X`

| Campo | Detalhe |
|---|---|
| **Área** | Carrinhos |
| **Prioridade** | 🟢 Baixa |
| **Esforço** | 2 pontos |

### Descrição

A API documenta que `GET /carrinhos` aceita filtro por `idUsuario`, mas a
suíte atual não testa esse comportamento. Validar que o filtro funciona
corretamente (retorna só o carrinho do usuário especificado) aumenta a
confiança na operação de listagem.

### Exemplo

```python
def test_filtrar_carrinhos_por_usuario(base_url, token_admin, produto_criado):
    """M03 — GET /carrinhos?idUsuario=X retorna só o carrinho do usuário."""
    from conftest import ADMIN_ID
    # Criar carrinho
    r = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r.status_code == 201

    # Filtrar por ID do usuário
    response = listar_carrinhos(base_url, params={"idUsuario": ADMIN_ID})
    assert response.status_code == 200
    body = response.json()
    assert body["quantidade"] == 1
    assert body["carrinhos"][0]["idUsuario"] == ADMIN_ID

    cancelar_compra(base_url, token_admin)
```

---

## M04 — Testar comportamento com token expirado

| Campo | Detalhe |
|---|---|
| **Área** | Autenticação |
| **Prioridade** | 🔴 Alta |
| **Esforço** | 3 pontos |

### Descrição

O token JWT da API expira em 600 segundos (10 minutos). A suíte não valida
o que acontece ao usar um token expirado em endpoints protegidos. O esperado
é 401 com mensagem `"Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"`.

Este teste é relevante para garantir que a expiração está funcionando e que
a mensagem de erro é consistente com o contrato.

### Exemplo

```python
def test_token_expirado_retorna_401(base_url):
    """M04 — Token JWT expirado deve retornar 401."""
    # Token JWT com exp no passado (gerado manualmente ou via biblioteca jwt)
    import jwt, time
    expired_payload = {
        "email": "fulano@qa.com",
        "password": "teste",
        "iat": int(time.time()) - 1200,
        "exp": int(time.time()) - 600,  # expirado há 600s
    }
    # Nota: requer a chave secreta do servidor para assinar — se não disponível,
    # usar token válido coletado em sessão anterior após aguardar 600s
    token_expirado = "Bearer " + jwt.encode(expired_payload, "secret", algorithm="HS256")

    import requests as req
    r = req.post(
        f"{base_url}/produtos",
        json=gerar_produto(),
        headers={"Authorization": token_expirado},
    )
    assert r.status_code == 401
```

---

## M05 — Validar bloqueio de exclusão de usuário com carrinho ativo

| Campo | Detalhe |
|---|---|
| **Área** | Usuários |
| **Prioridade** | 🔴 Alta |
| **Esforço** | 3 pontos |

### Descrição

A API deve impedir a exclusão de um usuário que possui carrinho ativo (assim
como impede a exclusão de produto com carrinho). A suíte atual não tem um
teste explícito para esse cenário em `/usuarios/{id}`. Essa validação garante
a integridade referencial da entidade carrinho.

### Exemplo

```python
def test_nao_excluir_usuario_com_carrinho_ativo(base_url, token_admin, produto_criado):
    """M05 — DELETE /usuarios/{id} com carrinho ativo deve retornar 400."""
    from conftest import ADMIN_ID
    # Criar carrinho para o usuário admin
    r_cart = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r_cart.status_code == 201

    # Tentar excluir o usuário
    import requests as req
    r_del = req.delete(f"{base_url}/usuarios/{ADMIN_ID}")
    assert r_del.status_code == 400
    assert "carrinho" in r_del.json()["message"].lower()

    cancelar_compra(base_url, token_admin)
```

---

## M06 — Testar campos em branco (`""`) vs. campo ausente

| Campo | Detalhe |
|---|---|
| **Área** | Geral (Usuários, Produtos) |
| **Prioridade** | 🟡 Média |
| **Esforço** | 2 pontos |

### Descrição

Existe diferença de comportamento entre enviar um campo com valor vazio (`""`)
e omitir o campo completamente do payload? Atualmente a suíte testa campos
ausentes, mas não campos em branco. Em algumas APIs, `"nome": ""` é tratado
diferente de não enviar o campo `nome`.

### Exemplo

```python
@pytest.mark.parametrize("campo,valor", [
    ("nome", ""),
    ("email", ""),
    ("password", ""),
])
def test_cadastrar_usuario_campo_em_branco_retorna_400(base_url, campo, valor):
    """M06 — Campo obrigatório em branco deve retornar 400."""
    from helpers.generators import gerar_email_unico
    base = {
        "nome": "Teste",
        "email": gerar_email_unico(),
        "password": "senha123",
        "administrador": "true",
    }
    base[campo] = valor
    response = criar_usuario(base_url, base)
    assert response.status_code == 400
```

---

## M07 — Parametrizar testes de campos obrigatórios

| Campo | Detalhe |
|---|---|
| **Área** | Refatoração (Usuários, Produtos, Login) |
| **Prioridade** | 🟢 Baixa |
| **Esforço** | 2 pontos |

### Descrição

Os testes de campos obrigatórios ausentes (U07, U08, U09) são estruturalmente
idênticos — variam apenas no campo omitido. Usar `@pytest.mark.parametrize`
reduziria duplicação e tornaria mais fácil adicionar novos campos no futuro.

### Exemplo de refatoração

```python
# Antes: 3 testes separados
def test_cadastrar_usuario_sem_nome_retorna_400(base_url): ...
def test_cadastrar_usuario_sem_email_retorna_400(base_url): ...
def test_cadastrar_usuario_sem_password_retorna_400(base_url): ...

# Depois: 1 teste parametrizado (mantém 3 casos de teste)
@pytest.mark.parametrize("campo_ausente", ["nome", "email", "password"])
def test_cadastrar_usuario_sem_campo_obrigatorio_retorna_400(base_url, campo_ausente):
    """M07 — Qualquer campo obrigatório ausente deve retornar 400."""
    from helpers.generators import gerar_email_unico
    payload = {
        "nome": "Teste",
        "email": gerar_email_unico(),
        "password": "senha123",
        "administrador": "true",
    }
    del payload[campo_ausente]
    response = criar_usuario(base_url, payload)
    assert response.status_code == 400
```

> **Atenção:** Esta refatoração deve ser feita de forma incremental. Os testes
> originais podem ser mantidos enquanto os parametrizados são validados.

---

## 📋 Resumo das Melhorias

| # | Descrição | Área | Prioridade | Esforço |
|---|---|---|---|---|
| M01 | Validar `preco=0` no cadastro de produto | Produtos | 🟡 Média | 1 pt |
| M02 | Testar `POST /carrinhos` sem token → 401 | Carrinhos | 🟡 Média | 1 pt |
| M03 | Verificar filtro `GET /carrinhos?idUsuario=X` | Carrinhos | 🟢 Baixa | 2 pt |
| M04 | Testar token JWT expirado → 401 | Autenticação | 🔴 Alta | 3 pt |
| M05 | Validar bloqueio de exclusão de usuário com carrinho | Usuários | 🔴 Alta | 3 pt |
| M06 | Testar campos em branco (`""`) vs. ausentes | Geral | 🟡 Média | 2 pt |
| M07 | Parametrizar testes de campos obrigatórios | Refactor | 🟢 Baixa | 2 pt |

**Total de esforço estimado:** 14 pontos de história
