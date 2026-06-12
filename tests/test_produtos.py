from helpers.produtos_helper import buscar_produto


def test_buscar_produto(
        base_url,
        produto_criado):
    response = buscar_produto(
        base_url,
        produto_criado["id"]
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == produto_criado["nome"]