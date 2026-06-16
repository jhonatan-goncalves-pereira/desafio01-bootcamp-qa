import jsonschema
from helpers.generators import gerar_produto
from helpers.produtos_helper import (
    listar_produtos,
    criar_produto,
    criar_produto_sem_token,
    buscar_produto,
    atualizar_produto,
    excluir_produto,
)
from helpers.carrinho_helper import criar_carrinho, cancelar_compra

PRODUTO_SCHEMA = {
    "type": "object",
    "required": ["nome", "preco", "descricao", "quantidade", "_id"],
    "properties": {
        "_id": {"type": "string"},
        "nome": {"type": "string"},
        "preco": {"type": "number"},
        "descricao": {"type": "string"},
        "quantidade": {"type": "integer"},
    },
}

LISTA_PRODUTOS_SCHEMA = {
    "type": "object",
    "required": ["quantidade", "produtos"],
    "properties": {
        "quantidade": {"type": "integer"},
        "produtos": {
            "type": "array",
            "items": PRODUTO_SCHEMA,
        },
    },
}

def test_listar_produtos_retorna_200(base_url):
    response = listar_produtos(base_url)

    assert response.status_code == 200
    body = response.json()
    assert "produtos" in body
    assert "quantidade" in body
    assert isinstance(body["produtos"], list)
    assert body["quantidade"] == len(body["produtos"])
    jsonschema.validate(instance=body, schema=LISTA_PRODUTOS_SCHEMA)

def test_listar_produtos_filtrar_por_nome(base_url, produto_criado):
    response = listar_produtos(base_url, params={"nome": produto_criado["nome"]})

    assert response.status_code == 200
    body = response.json()
    assert body["quantidade"] >= 1
    nomes = [p["nome"] for p in body["produtos"]]
    assert produto_criado["nome"] in nomes



def test_cadastrar_produto_com_token_admin_retorna_201(base_url, token_admin):
    payload = gerar_produto()
    response = criar_produto(base_url, token_admin, payload)

    assert response.status_code == 201
    body = response.json()
    assert "_id" in body
    assert body["message"] == "Cadastro realizado com sucesso"

    excluir_produto(base_url, token_admin, body["_id"])


def test_cadastrar_produto_sem_token_retorna_401(base_url):
    response = criar_produto_sem_token(base_url, gerar_produto())

    assert response.status_code == 401
    assert "message" in response.json()


def test_cadastrar_produto_com_token_nao_admin_retorna_403(base_url, token_nao_admin):
    response = criar_produto(base_url, token_nao_admin, gerar_produto())

    assert response.status_code == 403
    assert "message" in response.json()


def test_cadastrar_produto_com_nome_duplicado_retorna_400(base_url, token_admin, produto_criado):
    payload_duplicado = {
        "nome": produto_criado["nome"],
        "preco": 50,
        "descricao": "Descrição duplicada",
        "quantidade": 10,
    }
    response = criar_produto(base_url, token_admin, payload_duplicado)

    assert response.status_code == 400
    assert "message" in response.json()


def test_cadastrar_produto_token_invalido_retorna_401(base_url):
    import requests as req
    r = req.post(
        f"{base_url}/produtos",
        json=gerar_produto(),
        headers={"Authorization": "Bearer token_completamente_invalido_fake"},
    )
    assert r.status_code == 401


# ── BUG: Produto com quantidade=0 aceito mas inutilizável ─────────────────────


def test_criar_produto_quantidade_zero_aceito_mas_inutilizavel(base_url, token_admin):
    """P08 — [BUG #3] Produto com quantidade=0 é aceito no cadastro (201),
    mas ao tentar adicionar ao carrinho resulta em erro 400 por estoque
    insuficiente. O cadastro de produto com estoque zero deveria ser
    bloqueado ou ao menos alertado. Ver Issue #3.
    """
    payload = {**gerar_produto(), "quantidade": 0}
    response = criar_produto(base_url, token_admin, payload)

    # BUG: API aceita cadastro com estoque zero
    assert response.status_code == 201, "API deveria aceitar (BUG documentado)"
    produto_id = response.json()["_id"]

    # Garantir que não há carrinho ativo (estado sujo de teste anterior)
    cancelar_compra(base_url, token_admin)

    # Consequência: produto não pode ser usado no carrinho
    r_carrinho = criar_carrinho(base_url, token_admin, produto_id)
    assert r_carrinho.status_code == 400
    assert "quantidade suficiente" in r_carrinho.json()["message"]

    excluir_produto(base_url, token_admin, produto_id)


def test_criar_produto_quantidade_como_string_aceito(base_url, token_admin):
    """P09 — [BUG #4] Campo 'quantidade' aceita string numérica ('10') quando
    deveria exigir apenas inteiro. A API converte silenciosamente em vez de
    rejeitar. Ver Issue #4.
    """
    import requests as req
    payload = {
        "nome": f"ProdQtdString {__import__('uuid').uuid4().hex[:6]}",
        "preco": 10,
        "descricao": "teste",
        "quantidade": "10", 
    }
    r = req.post(f"{base_url}/produtos", json=payload, headers={"Authorization": token_admin})

    # BUG: API aceita e retorna 201 em vez de rejeitar com 400
    assert r.status_code == 201, "BUG confirmado: quantidade como string foi aceita"
    excluir_produto(base_url, token_admin, r.json()["_id"])


def test_criar_produto_preco_float_retorna_400(base_url, token_admin):
    """P10 — Preço float (ex: 10.99) é rejeitado com 400.

    A API só aceita inteiros no campo 'preco'. Isso pode surpreender
    integradores que esperam suporte a centavos.
    """
    payload = {**gerar_produto(), "preco": 10.99}
    response = criar_produto(base_url, token_admin, payload)

    assert response.status_code == 400
    assert "preco" in response.json()


def test_criar_produto_preco_negativo_retorna_400(base_url, token_admin):
    payload = {**gerar_produto(), "preco": -1}
    response = criar_produto(base_url, token_admin, payload)

    assert response.status_code == 400


def test_criar_produto_quantidade_negativa_retorna_400(base_url, token_admin):
    payload = {**gerar_produto(), "quantidade": -1}
    response = criar_produto(base_url, token_admin, payload)

    assert response.status_code == 400


def test_buscar_produto_por_id_valido_retorna_200(base_url, produto_criado):
    response = buscar_produto(base_url, produto_criado["id"])

    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == produto_criado["nome"]
    assert body["_id"] == produto_criado["id"]
    jsonschema.validate(instance=body, schema=PRODUTO_SCHEMA)


def test_buscar_produto_por_id_formato_invalido_retorna_400(base_url):
    """P14 — GET /produtos/{id} com ID de formato inválido (< 16 chars) retorna 400.

    BUG DOCUMENTADO (Issue #1): retorna {'id': '...'} em vez de {'message': '...'},
    quebrando a consistência do contrato de erro da API.
    """
    response = buscar_produto(base_url, "id_invalido")

    assert response.status_code == 400
    body = response.json()
    assert "id" in body


def test_buscar_produto_por_id_inexistente_retorna_400(base_url):
    response = buscar_produto(base_url, "aaaaaaaaaaaaaaaa")  # 16 chars, não existe

    assert response.status_code == 400
    assert "message" in response.json()


def test_atualizar_produto_existente_retorna_200(base_url, token_admin, produto_criado):
    payload_atualizado = {
        "nome": f"{produto_criado['nome']} Atualizado",
        "preco": 200,
        "descricao": "Descrição atualizada pelo QA",
        "quantidade": 30,
    }
    response = atualizar_produto(base_url, token_admin, produto_criado["id"], payload_atualizado)

    assert response.status_code == 200
    assert response.json()["message"] == "Registro alterado com sucesso"


def test_atualizar_produto_com_nome_de_outro_produto_retorna_400(base_url, token_admin):
    import uuid
    nome_fixo = f"NomeFixo {uuid.uuid4().hex[:6]}"

    # Criar produto A com o nome fixo
    r_a = criar_produto(base_url, token_admin, {**gerar_produto(), "nome": nome_fixo})
    assert r_a.status_code == 201, f"Falha ao criar produto A: {r_a.json()}"
    pid_a = r_a.json()["_id"]

    # Criar produto B com nome genérico
    r_b = criar_produto(base_url, token_admin, gerar_produto())
    assert r_b.status_code == 201, f"Falha ao criar produto B: {r_b.json()}"
    pid_b = r_b.json()["_id"]

    # Tentar renomear B para o mesmo nome de A → deve retornar 400
    response = atualizar_produto(base_url, token_admin, pid_b, {**gerar_produto(), "nome": nome_fixo})

    assert response.status_code == 400
    assert "message" in response.json()

    excluir_produto(base_url, token_admin, pid_a)
    excluir_produto(base_url, token_admin, pid_b)


def test_atualizar_produto_inexistente_cria_novo(base_url, token_admin):
    payload = gerar_produto()
    response = atualizar_produto(base_url, token_admin, "aaaaaaaaaaaaaaaa", payload)

    assert response.status_code == 201
    body = response.json()
    assert "_id" in body

    excluir_produto(base_url, token_admin, body["_id"])


def test_excluir_produto_existente_retorna_200(base_url, token_admin):
    r = criar_produto(base_url, token_admin, gerar_produto())
    assert r.status_code == 201
    produto_id = r.json()["_id"]

    response = excluir_produto(base_url, token_admin, produto_id)

    assert response.status_code == 200
    assert response.json()["message"] == "Registro excluído com sucesso"


def test_excluir_produto_com_carrinho_ativo_retorna_400(base_url, token_admin, produto_criado):
    
    carrinho = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert carrinho.status_code == 201

    response = excluir_produto(base_url, token_admin, produto_criado["id"])

    assert response.status_code == 400
    assert "message" in response.json()

    cancelar_compra(base_url, token_admin)
