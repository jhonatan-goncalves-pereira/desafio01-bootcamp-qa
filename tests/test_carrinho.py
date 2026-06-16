import jsonschema
from helpers.carrinho_helper import (
    listar_carrinhos,
    criar_carrinho,
    buscar_carrinho,
    cancelar_compra,
    concluir_compra,
)
from helpers.produtos_helper import criar_produto, excluir_produto
from helpers.generators import gerar_produto

CARRINHO_SCHEMA = {
    "type": "object",
    "required": ["produtos", "precoTotal", "quantidadeTotal", "idUsuario", "_id"],
    "properties": {
        "_id": {"type": "string"},
        "precoTotal": {"type": "number"},
        "quantidadeTotal": {"type": "integer"},
        "idUsuario": {"type": "string"},
        "produtos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["idProduto", "quantidade", "precoUnitario"],
                "properties": {
                    "idProduto": {"type": "string"},
                    "quantidade": {"type": "integer"},
                    "precoUnitario": {"type": "number"},
                },
            },
        },
    },
}

LISTA_CARRINHOS_SCHEMA = {
    "type": "object",
    "required": ["quantidade", "carrinhos"],
    "properties": {
        "quantidade": {"type": "integer"},
        "carrinhos": {"type": "array"},
    },
}

def test_listar_carrinhos_retorna_200(base_url):
    response = listar_carrinhos(base_url)

    assert response.status_code == 200
    body = response.json()
    assert "carrinhos" in body
    assert "quantidade" in body
    assert isinstance(body["carrinhos"], list)
    jsonschema.validate(instance=body, schema=LISTA_CARRINHOS_SCHEMA)

def test_criar_carrinho_com_sucesso(base_url, token_admin, produto_criado):
    response = criar_carrinho(base_url, token_admin, produto_criado["id"])
    body = response.json()

    assert response.status_code == 201
    assert "_id" in body
    assert body["message"] == "Cadastro realizado com sucesso"

    cancelar_compra(base_url, token_admin)


def test_criar_carrinho_valida_schema_do_carrinho(base_url, token_admin, produto_criado):
    r = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r.status_code == 201
    carrinho_id = r.json()["_id"]

    response = buscar_carrinho(base_url, carrinho_id)
    assert response.status_code == 200
    jsonschema.validate(instance=response.json(), schema=CARRINHO_SCHEMA)

    cancelar_compra(base_url, token_admin)


def test_nao_permitir_dois_carrinhos_para_mesmo_usuario(base_url, token_admin, produto_criado):
    primeira = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert primeira.status_code == 201

    segunda = criar_carrinho(base_url, token_admin, produto_criado["id"])

    assert segunda.status_code == 400
    assert "Não é permitido ter mais de 1 carrinho" in segunda.json()["message"]

    cancelar_compra(base_url, token_admin)


def test_criar_carrinho_com_produto_inexistente_retorna_400(base_url, token_admin):
    response = criar_carrinho(base_url, token_admin, "produto_id_invalido_xx")

    assert response.status_code == 400
    assert "Produto não encontrado" in response.json()["message"]


def test_criar_carrinho_quantidade_acima_do_estoque_retorna_400(base_url, token_admin):
    payload = {**gerar_produto(), "quantidade": 2}
    r = criar_produto(base_url, token_admin, payload)
    assert r.status_code == 201
    pid = r.json()["_id"]

    response = criar_carrinho(base_url, token_admin, pid, quantidade=10)

    assert response.status_code == 400
    body = response.json()
    assert "message" in body
    assert "quantidade suficiente" in body["message"]
    assert "item" in body

    excluir_produto(base_url, token_admin, pid)


def test_criar_carrinho_com_produto_duplicado_retorna_400(base_url, token_admin, produto_criado):
    import requests as req
    r = req.post(
        f"{base_url}/carrinhos",
        json={
            "produtos": [
                {"idProduto": produto_criado["id"], "quantidade": 1},
                {"idProduto": produto_criado["id"], "quantidade": 2},
            ]
        },
        headers={"Authorization": token_admin},
    )

    assert r.status_code == 400
    body = r.json()
    assert "message" in body
    assert "duplicado" in body["message"].lower()


def test_buscar_carrinho_por_id_retorna_200(base_url, token_admin, produto_criado):
    r = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r.status_code == 201
    carrinho_id = r.json()["_id"]

    response = buscar_carrinho(base_url, carrinho_id)
    body = response.json()

    assert response.status_code == 200
    assert body["_id"] == carrinho_id

    cancelar_compra(base_url, token_admin)


def test_buscar_carrinho_inexistente_retorna_400(base_url):
    response = buscar_carrinho(base_url, "id_inexistente_xyz")

    assert response.status_code == 400


def test_cancelar_compra_retorna_200(base_url, token_admin, produto_criado):
    r = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r.status_code == 201

    response = cancelar_compra(base_url, token_admin)

    assert response.status_code == 200


def test_concluir_compra_retorna_200(base_url, token_admin, produto_criado):
    r = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r.status_code == 201

    response = concluir_compra(base_url, token_admin)

    assert response.status_code == 200
    assert response.json()["message"] == "Registro excluído com sucesso"


def test_concluir_compra_sem_carrinho_retorna_200_com_aviso(base_url, token_admin):
    """C12 — [BUG #5] DELETE /concluir-compra sem carrinho ativo retorna 200.

    Semanticamente, uma operação sobre recurso inexistente deveria retornar
    404 (Not Found). A API retorna 200 com mensagem de aviso, o que pode
    levar clientes a interpretar erroneamente o sucesso da operação.
    Ver Issue #5.
    """
    # Garante que não há carrinho
    cancelar_compra(base_url, token_admin)

    response = concluir_compra(base_url, token_admin)

    assert response.status_code == 200
    body = response.json()
    assert "Não foi encontrado carrinho" in body["message"]


def test_cancelar_compra_sem_carrinho_retorna_200_com_aviso(base_url, token_admin):
    """C13 — [BUG #5] DELETE /cancelar-compra sem carrinho ativo retorna 200.

    Mesmo comportamento semanticamente incorreto do teste C12.
    Ver Issue #5.
    """
    # Garante que não há carrinho
    cancelar_compra(base_url, token_admin)

    response = cancelar_compra(base_url, token_admin)

    assert response.status_code == 200
    body = response.json()
    assert "Não foi encontrado carrinho" in body["message"]


def test_cancelar_compra_devolve_estoque_ao_produto(base_url, token_admin):
    import requests as req

    payload = {**gerar_produto(), "quantidade": 5}
    r = criar_produto(base_url, token_admin, payload)
    assert r.status_code == 201
    pid = r.json()["_id"]

    r_cart = criar_carrinho(base_url, token_admin, pid, quantidade=2)
    assert r_cart.status_code == 201
    from helpers.produtos_helper import buscar_produto
    estoque_apos_criacao = buscar_produto(base_url, pid).json()["quantidade"]
    assert estoque_apos_criacao == 3, f"Estoque esperado=3, obtido={estoque_apos_criacao}"

    cancelar_compra(base_url, token_admin)

    estoque_apos_cancelamento = buscar_produto(base_url, pid).json()["quantidade"]
    assert estoque_apos_cancelamento == 5, (
        f"Estoque não foi restaurado. Esperado=5, obtido={estoque_apos_cancelamento}"
    )

    excluir_produto(base_url, token_admin, pid)
