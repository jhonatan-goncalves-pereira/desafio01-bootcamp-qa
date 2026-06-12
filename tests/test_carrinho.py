from helpers.carrinho_helper import (criar_carrinho,buscar_carrinho,cancelar_compra,concluir_compra)

def test_criar_carrinho_com_sucesso(base_url,token_admin,produto_criado):
    response = criar_carrinho(base_url,token_admin,produto_criado["id"])
    body = response.json()
    assert response.status_code == 201
    assert "_id" in body
    assert body["message"] == "Cadastro realizado com sucesso"
    cancelar_compra(base_url,token_admin)


def test_buscar_carrinho_por_id_retorna_200(base_url,token_admin,produto_criado):
    criacao = criar_carrinho(base_url,token_admin,produto_criado["id"])
    assert criacao.status_code == 201
    carrinho_id = criacao.json()["_id"]
    response = buscar_carrinho(base_url,carrinho_id)
    body = response.json()
    assert response.status_code == 200
    assert body["_id"] == carrinho_id
    cancelar_compra(base_url,token_admin)

def test_buscar_carrinho_inexistente_retorna_400(base_url):
    response = buscar_carrinho(base_url,"id_inexistente_xyz")
    assert response.status_code == 400
    #assert response.json()["message"] == "Carrinho não encontrado"


def test_nao_permitir_dois_carrinhos_para_mesmo_usuario(base_url,token_admin,produto_criado):
    primeira = criar_carrinho(base_url,token_admin,produto_criado["id"])
    assert primeira.status_code == 201
    segunda = criar_carrinho(base_url,token_admin,produto_criado["id"])
    assert segunda.status_code == 400
    assert ("Não é permitido ter mais de 1 carrinho"in segunda.json()["message"])
    cancelar_compra(base_url,token_admin)

def test_criar_carrinho_com_produto_inexistente_retorna_400(base_url,token_admin):
    response = criar_carrinho(base_url,token_admin,"produto_inexistente")
    assert response.status_code == 400
    assert ("Produto não encontrado"in response.json()["message"])

def test_cancelar_compra_retorna_200(base_url,token_admin,produto_criado):
    criacao = criar_carrinho(base_url,token_admin,produto_criado["id"])
    assert criacao.status_code == 201
    response = cancelar_compra(base_url,token_admin)
    assert response.status_code == 200
    #assert response.json()["message"] == "Registro excluído com sucesso"


def test_concluir_compra_retorna_200(base_url,token_admin,produto_criado):
    criacao = criar_carrinho(base_url,token_admin,produto_criado["id"])
    assert criacao.status_code == 201
    response = concluir_compra(base_url,token_admin)
    assert response.status_code == 200
    assert response.json()["message"] == "Registro excluído com sucesso"