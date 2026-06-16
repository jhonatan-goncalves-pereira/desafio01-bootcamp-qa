import allure
import jsonschema
from helpers.generators import gerar_produto
from helpers.produtos_helper import (
    listar_produtos, criar_produto, criar_produto_sem_token,
    buscar_produto, atualizar_produto, excluir_produto,
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
        "produtos": {"type": "array", "items": PRODUTO_SCHEMA},
    },
}


@allure.epic("ServeRest API")
@allure.feature("Produtos")
class TestProdutos:

    @allure.story("Listagem")
    @allure.title("P01 - GET /produtos retorna 200 e schema valido")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_listar_produtos_retorna_200(self, base_url):
        with allure.step("Chamar GET /produtos"):
            response = listar_produtos(base_url)
        with allure.step("Validar 200, campos e JSON Schema"):
            assert response.status_code == 200
            body = response.json()
            allure.attach(str(body)[:200], name="Response", attachment_type=allure.attachment_type.JSON)
            assert "produtos" in body
            assert "quantidade" in body
            assert body["quantidade"] == len(body["produtos"])
            jsonschema.validate(instance=body, schema=LISTA_PRODUTOS_SCHEMA)

    @allure.story("Listagem")
    @allure.title("P02 - Filtrar por nome retorna produto correspondente")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo")
    def test_listar_produtos_filtrar_por_nome(self, base_url, produto_criado):
        with allure.step("Chamar GET /produtos?nome=X"):
            response = listar_produtos(base_url, params={"nome": produto_criado["nome"]})
        with allure.step("Validar que produto aparece no resultado"):
            assert response.status_code == 200
            body = response.json()
            assert body["quantidade"] >= 1
            assert produto_criado["nome"] in [p["nome"] for p in body["produtos"]]

    @allure.story("Cadastro")
    @allure.title("P03 - Criar com token admin retorna 201")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_cadastrar_produto_com_token_admin_retorna_201(self, base_url, token_admin):
        with allure.step("POST /produtos com token de admin"):
            payload = gerar_produto()
            response = criar_produto(base_url, token_admin, payload)
        with allure.step("Validar 201 e _id"):
            assert response.status_code == 201
            body = response.json()
            allure.attach(str(body), name="Produto Criado", attachment_type=allure.attachment_type.JSON)
            assert "_id" in body
        excluir_produto(base_url, token_admin, body["_id"])

    @allure.story("Autenticacao")
    @allure.title("P04 - Criar sem token retorna 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "seguranca")
    def test_cadastrar_produto_sem_token_retorna_401(self, base_url):
        with allure.step("POST /produtos sem Authorization header"):
            response = criar_produto_sem_token(base_url, gerar_produto())
        with allure.step("Validar 401"):
            assert response.status_code == 401
            assert "message" in response.json()

    @allure.story("Autenticacao")
    @allure.title("P05 - Criar com token nao-admin retorna 403")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "seguranca")
    def test_cadastrar_produto_com_token_nao_admin_retorna_403(self, base_url, token_nao_admin):
        with allure.step("POST /produtos com token de usuario comum"):
            response = criar_produto(base_url, token_nao_admin, gerar_produto())
        with allure.step("Validar 403"):
            assert response.status_code == 403
            assert "message" in response.json()

    @allure.story("Cadastro")
    @allure.title("P06 - Nome duplicado retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_cadastrar_produto_com_nome_duplicado_retorna_400(self, base_url, token_admin, produto_criado):
        with allure.step("POST /produtos com nome ja existente"):
            payload = {"nome": produto_criado["nome"], "preco": 50, "descricao": "dup", "quantidade": 10}
            response = criar_produto(base_url, token_admin, payload)
        with allure.step("Validar 400"):
            assert response.status_code == 400
            assert "message" in response.json()

    @allure.story("Autenticacao")
    @allure.title("P07 - Token completamente invalido retorna 401")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo", "seguranca")
    def test_cadastrar_produto_token_invalido_retorna_401(self, base_url):
        import requests as req
        with allure.step("POST /produtos com token fake"):
            r = req.post(f"{base_url}/produtos", json=gerar_produto(), headers={"Authorization": "Bearer token_fake_invalido"})
        with allure.step("Validar 401"):
            assert r.status_code == 401

    @allure.story("Validacao de entrada")
    @allure.title("P08 - quantidade=0 aceito no cadastro mas bloqueia no carrinho [BUG #3]")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("bug", "regressao")
    @allure.issue("3", "BUG #3 - quantidade=0 aceita silenciosamente")
    def test_criar_produto_quantidade_zero_aceito_mas_inutilizavel(self, base_url, token_admin):
        with allure.step("POST /produtos com quantidade=0"):
            payload = {**gerar_produto(), "quantidade": 0}
            response = criar_produto(base_url, token_admin, payload)
            assert response.status_code == 201
            produto_id = response.json()["_id"]
            allure.attach("BUG: API aceita estoque zero", name="Bug Note", attachment_type=allure.attachment_type.TEXT)
        cancelar_compra(base_url, token_admin)
        with allure.step("Tentar adicionar ao carrinho - deve falhar com 400"):
            r_carrinho = criar_carrinho(base_url, token_admin, produto_id)
            assert r_carrinho.status_code == 400
            assert "quantidade suficiente" in r_carrinho.json()["message"]
        excluir_produto(base_url, token_admin, produto_id)

    @allure.story("Validacao de entrada")
    @allure.title("P09 - quantidade como string aceita silenciosamente [BUG #4]")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("bug", "regressao")
    @allure.issue("4", "BUG #4 - Coercao silenciosa de tipos")
    def test_criar_produto_quantidade_como_string_aceito(self, base_url, token_admin):
        import requests as req, uuid
        with allure.step("POST /produtos com quantidade como string numerica"):
            payload = {"nome": f"ProdQtdStr {uuid.uuid4().hex[:6]}", "preco": 10, "descricao": "teste", "quantidade": "10"}
            r = req.post(f"{base_url}/produtos", json=payload, headers={"Authorization": token_admin})
            allure.attach("BUG: string aceita sem erro", name="Bug Note", attachment_type=allure.attachment_type.TEXT)
            assert r.status_code == 201
            excluir_produto(base_url, token_admin, r.json()["_id"])

    @allure.story("Validacao de entrada")
    @allure.title("P10 - Preco float retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_produto_preco_float_retorna_400(self, base_url, token_admin):
        with allure.step("POST /produtos com preco=10.99"):
            payload = {**gerar_produto(), "preco": 10.99}
            response = criar_produto(base_url, token_admin, payload)
        with allure.step("Validar 400"):
            assert response.status_code == 400
            assert "preco" in response.json()

    @allure.story("Validacao de entrada")
    @allure.title("P11 - Preco negativo retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_produto_preco_negativo_retorna_400(self, base_url, token_admin):
        payload = {**gerar_produto(), "preco": -1}
        response = criar_produto(base_url, token_admin, payload)
        assert response.status_code == 400

    @allure.story("Validacao de entrada")
    @allure.title("P12 - quantidade negativa retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_produto_quantidade_negativa_retorna_400(self, base_url, token_admin):
        payload = {**gerar_produto(), "quantidade": -1}
        response = criar_produto(base_url, token_admin, payload)
        assert response.status_code == 400

    @allure.story("Busca por ID")
    @allure.title("P13 - Buscar por ID valido retorna 200 e schema")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_buscar_produto_por_id_valido_retorna_200(self, base_url, produto_criado):
        with allure.step("GET /produtos/{id} com ID valido"):
            response = buscar_produto(base_url, produto_criado["id"])
        with allure.step("Validar 200, nome e schema"):
            assert response.status_code == 200
            body = response.json()
            assert body["nome"] == produto_criado["nome"]
            jsonschema.validate(instance=body, schema=PRODUTO_SCHEMA)

    @allure.story("Busca por ID")
    @allure.title("P14 - ID formato invalido retorna 400 [BUG #1]")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negativo", "bug")
    @allure.issue("1", "BUG #1 - Contrato de erro inconsistente")
    def test_buscar_produto_por_id_formato_invalido_retorna_400(self, base_url):
        with allure.step("GET /produtos/id_invalido"):
            response = buscar_produto(base_url, "id_invalido")
        with allure.step("Validar 400 e chave id na resposta"):
            assert response.status_code == 400
            assert "id" in response.json()

    @allure.story("Busca por ID")
    @allure.title("P15 - ID inexistente retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_buscar_produto_por_id_inexistente_retorna_400(self, base_url):
        response = buscar_produto(base_url, "aaaaaaaaaaaaaaaa")
        assert response.status_code == 400
        assert "message" in response.json()

    @allure.story("Atualizacao")
    @allure.title("P16 - Atualizar existente retorna 200")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo")
    def test_atualizar_produto_existente_retorna_200(self, base_url, token_admin, produto_criado):
        with allure.step("PUT /produtos/{id} com novo payload"):
            payload = {"nome": f"{produto_criado['nome']} Atualizado", "preco": 200, "descricao": "Atualizado QA", "quantidade": 30}
            response = atualizar_produto(base_url, token_admin, produto_criado["id"], payload)
        with allure.step("Validar 200"):
            assert response.status_code == 200
            assert response.json()["message"] == "Registro alterado com sucesso"

    @allure.story("Atualizacao")
    @allure.title("P17 - Atualizar com nome de outro produto retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_atualizar_produto_com_nome_de_outro_produto_retorna_400(self, base_url, token_admin):
        import uuid
        nome_fixo = f"NomeFixo {uuid.uuid4().hex[:6]}"
        with allure.step("Criar produto A com nome fixo"):
            r_a = criar_produto(base_url, token_admin, {**gerar_produto(), "nome": nome_fixo})
            assert r_a.status_code == 201
            pid_a = r_a.json()["_id"]
        with allure.step("Criar produto B com nome generico"):
            r_b = criar_produto(base_url, token_admin, gerar_produto())
            assert r_b.status_code == 201
            pid_b = r_b.json()["_id"]
        with allure.step("Tentar renomear B para o nome de A - deve retornar 400"):
            response = atualizar_produto(base_url, token_admin, pid_b, {**gerar_produto(), "nome": nome_fixo})
            assert response.status_code == 400
        excluir_produto(base_url, token_admin, pid_a)
        excluir_produto(base_url, token_admin, pid_b)

    @allure.story("Atualizacao")
    @allure.title("P18 - PUT em ID inexistente cria produto upsert 201")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("borda")
    def test_atualizar_produto_inexistente_cria_novo(self, base_url, token_admin):
        with allure.step("PUT /produtos com ID inexistente"):
            response = atualizar_produto(base_url, token_admin, "aaaaaaaaaaaaaaaa", gerar_produto())
        with allure.step("Validar upsert 201"):
            assert response.status_code == 201
            body = response.json()
            assert "_id" in body
        excluir_produto(base_url, token_admin, body["_id"])

    @allure.story("Exclusao")
    @allure.title("P19 - Excluir produto sem carrinho retorna 200")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo")
    def test_excluir_produto_existente_retorna_200(self, base_url, token_admin):
        with allure.step("Criar produto para excluir"):
            r = criar_produto(base_url, token_admin, gerar_produto())
            assert r.status_code == 201
            produto_id = r.json()["_id"]
        with allure.step("DELETE /produtos/{id}"):
            response = excluir_produto(base_url, token_admin, produto_id)
        with allure.step("Validar 200"):
            assert response.status_code == 200
            assert response.json()["message"] == "Registro excluido com sucesso"

    @allure.story("Exclusao")
    @allure.title("P20 - Excluir produto com carrinho ativo retorna 400")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "integridade")
    def test_excluir_produto_com_carrinho_ativo_retorna_400(self, base_url, token_admin, produto_criado):
        with allure.step("Criar carrinho com o produto"):
            carrinho = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert carrinho.status_code == 201
        with allure.step("Tentar excluir produto com carrinho ativo"):
            response = excluir_produto(base_url, token_admin, produto_criado["id"])
        with allure.step("Validar 400"):
            assert response.status_code == 400
            assert "message" in response.json()
        cancelar_compra(base_url, token_admin)