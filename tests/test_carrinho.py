import allure
import jsonschema
from helpers.carrinho_helper import (
    listar_carrinhos, criar_carrinho, buscar_carrinho,
    cancelar_compra, concluir_compra,
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


@allure.epic("ServeRest API")
@allure.feature("Carrinhos")
class TestCarrinhos:

    @allure.story("Listagem")
    @allure.title("C01 - GET /carrinhos retorna 200 e schema valido")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_listar_carrinhos_retorna_200(self, base_url):
        with allure.step("Chamar GET /carrinhos"):
            response = listar_carrinhos(base_url)
        with allure.step("Validar 200 e JSON Schema"):
            assert response.status_code == 200
            body = response.json()
            allure.attach(str(body)[:200], name="Response", attachment_type=allure.attachment_type.JSON)
            assert "carrinhos" in body
            assert "quantidade" in body
            jsonschema.validate(instance=body, schema=LISTA_CARRINHOS_SCHEMA)

    @allure.story("Criacao de carrinho")
    @allure.title("C02 - Criar carrinho com produto valido retorna 201")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_criar_carrinho_com_sucesso(self, base_url, token_admin, produto_criado):
        with allure.step("POST /carrinhos com produto valido"):
            response = criar_carrinho(base_url, token_admin, produto_criado["id"])
            body = response.json()
        with allure.step("Validar 201 e _id"):
            assert response.status_code == 201
            assert "_id" in body
            allure.attach(str(body), name="Carrinho Criado", attachment_type=allure.attachment_type.JSON)
        cancelar_compra(base_url, token_admin)

    @allure.story("Criacao de carrinho")
    @allure.title("C03 - Schema do carrinho criado e valido")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo", "contrato")
    def test_criar_carrinho_valida_schema_do_carrinho(self, base_url, token_admin, produto_criado):
        cancelar_compra(base_url, token_admin)  # garante estado limpo
        with allure.step("Criar carrinho e buscar por ID"):
            r = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert r.status_code == 201
            carrinho_id = r.json()["_id"]
            response = buscar_carrinho(base_url, carrinho_id)
        with allure.step("Validar JSON Schema do carrinho"):
            assert response.status_code == 200
            jsonschema.validate(instance=response.json(), schema=CARRINHO_SCHEMA)
        cancelar_compra(base_url, token_admin)

    @allure.story("Restricoes de negocio")
    @allure.title("C04 - Segundo carrinho para mesmo usuario retorna 400")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo")
    def test_nao_permitir_dois_carrinhos_para_mesmo_usuario(self, base_url, token_admin, produto_criado):
        with allure.step("Criar primeiro carrinho"):
            primeira = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert primeira.status_code == 201
        with allure.step("Tentar criar segundo carrinho - deve retornar 400"):
            segunda = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert segunda.status_code == 400
            assert "Nao e permitido ter mais de 1 carrinho" in segunda.json()["message"] or "permitido" in segunda.json()["message"].lower()
        cancelar_compra(base_url, token_admin)

    @allure.story("Restricoes de negocio")
    @allure.title("C05 - Produto inexistente no carrinho retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_carrinho_com_produto_inexistente_retorna_400(self, base_url, token_admin):
        with allure.step("POST /carrinhos com produto inexistente"):
            response = criar_carrinho(base_url, token_admin, "produto_id_invalido_xx")
        with allure.step("Validar 400 e mensagem"):
            assert response.status_code == 400
            assert "Produto nao encontrado" in response.json()["message"] or "encontrado" in response.json()["message"].lower()

    @allure.story("Restricoes de negocio")
    @allure.title("C06 - Quantidade acima do estoque retorna 400 com detalhe")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_carrinho_quantidade_acima_do_estoque_retorna_400(self, base_url, token_admin):
        with allure.step("Criar produto com estoque = 2"):
            payload = {**gerar_produto(), "quantidade": 2}
            r = criar_produto(base_url, token_admin, payload)
            assert r.status_code == 201
            pid = r.json()["_id"]
        with allure.step("Tentar adicionar 10 unidades - deve retornar 400"):
            response = criar_carrinho(base_url, token_admin, pid, quantidade=10)
            assert response.status_code == 400
            body = response.json()
            allure.attach(str(body), name="Erro Estoque", attachment_type=allure.attachment_type.JSON)
            assert "quantidade suficiente" in body["message"]
            assert "item" in body
        excluir_produto(base_url, token_admin, pid)

    @allure.story("Restricoes de negocio")
    @allure.title("C07 - Produto duplicado no array retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_criar_carrinho_com_produto_duplicado_retorna_400(self, base_url, token_admin, produto_criado):
        import requests as req
        with allure.step("POST /carrinhos com mesmo produto duas vezes"):
            r = req.post(
                f"{base_url}/carrinhos",
                json={"produtos": [
                    {"idProduto": produto_criado["id"], "quantidade": 1},
                    {"idProduto": produto_criado["id"], "quantidade": 2},
                ]},
                headers={"Authorization": token_admin},
            )
        with allure.step("Validar 400 e mensagem de duplicado"):
            assert r.status_code == 400
            assert "duplicado" in r.json()["message"].lower()

    @allure.story("Busca por ID")
    @allure.title("C08 - Buscar carrinho por ID retorna 200")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo")
    def test_buscar_carrinho_por_id_retorna_200(self, base_url, token_admin, produto_criado):
        with allure.step("Criar carrinho e buscar pelo ID"):
            r = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert r.status_code == 201
            carrinho_id = r.json()["_id"]
            response = buscar_carrinho(base_url, carrinho_id)
        with allure.step("Validar 200 e _id correto"):
            assert response.status_code == 200
            assert response.json()["_id"] == carrinho_id
        cancelar_compra(base_url, token_admin)

    @allure.story("Busca por ID")
    @allure.title("C09 - Buscar carrinho inexistente retorna 400")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negativo")
    def test_buscar_carrinho_inexistente_retorna_400(self, base_url):
        with allure.step("GET /carrinhos com ID invalido"):
            response = buscar_carrinho(base_url, "id_inexistente_xyz")
        with allure.step("Validar 400"):
            assert response.status_code == 400

    @allure.story("Fluxo de compra")
    @allure.title("C10 - Cancelar compra com carrinho ativo retorna 200")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_cancelar_compra_retorna_200(self, base_url, token_admin, produto_criado):
        with allure.step("Criar carrinho"):
            r = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert r.status_code == 201
        with allure.step("DELETE /carrinhos/cancelar-compra"):
            response = cancelar_compra(base_url, token_admin)
        with allure.step("Validar 200"):
            assert response.status_code == 200

    @allure.story("Fluxo de compra")
    @allure.title("C11 - Concluir compra com carrinho ativo retorna 200")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_concluir_compra_retorna_200(self, base_url, token_admin, produto_criado):
        with allure.step("Criar carrinho"):
            r = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert r.status_code == 201
        with allure.step("DELETE /carrinhos/concluir-compra"):
            response = concluir_compra(base_url, token_admin)
        with allure.step("Validar 200"):
            assert response.status_code == 200
            assert response.json()["message"] == "Registro exclu\u00eddo com sucesso"

    @allure.story("Fluxo de compra")
    @allure.title("C12 - Concluir sem carrinho retorna 200 com aviso [BUG #5]")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("bug", "regressao")
    @allure.issue("5", "BUG #5 - DELETE sem carrinho retorna 200 em vez de 404")
    def test_concluir_compra_sem_carrinho_retorna_200_com_aviso(self, base_url, token_admin):
        with allure.step("Garantir que nao ha carrinho ativo"):
            cancelar_compra(base_url, token_admin)
        with allure.step("DELETE /carrinhos/concluir-compra sem carrinho"):
            response = concluir_compra(base_url, token_admin)
        with allure.step("Confirmar BUG: 200 com mensagem de nao encontrado"):
            assert response.status_code == 200
            allure.attach("BUG: deveria ser 404", name="Bug Note", attachment_type=allure.attachment_type.TEXT)
            assert "Nao foi encontrado carrinho" in response.json()["message"] or "encontrado" in response.json()["message"].lower()

    @allure.story("Fluxo de compra")
    @allure.title("C13 - Cancelar sem carrinho retorna 200 com aviso [BUG #5]")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("bug", "regressao")
    @allure.issue("5", "BUG #5 - DELETE sem carrinho retorna 200 em vez de 404")
    def test_cancelar_compra_sem_carrinho_retorna_200_com_aviso(self, base_url, token_admin):
        with allure.step("Garantir ausencia de carrinho"):
            cancelar_compra(base_url, token_admin)
        with allure.step("DELETE /carrinhos/cancelar-compra sem carrinho"):
            response = cancelar_compra(base_url, token_admin)
        with allure.step("Confirmar BUG: 200 com mensagem de nao encontrado"):
            assert response.status_code == 200
            assert "encontrado" in response.json()["message"].lower()

    @allure.story("Fluxo de compra")
    @allure.title("C14 - Cancelar compra restaura estoque do produto")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "regressao")
    def test_cancelar_compra_devolve_estoque_ao_produto(self, base_url, token_admin):
        from helpers.produtos_helper import buscar_produto
        with allure.step("Criar produto com estoque = 5"):
            payload = {**gerar_produto(), "quantidade": 5}
            r = criar_produto(base_url, token_admin, payload)
            assert r.status_code == 201
            pid = r.json()["_id"]
        with allure.step("Adicionar 2 unidades ao carrinho"):
            r_cart = criar_carrinho(base_url, token_admin, pid, quantidade=2)
            assert r_cart.status_code == 201
            estoque_apos = buscar_produto(base_url, pid).json()["quantidade"]
            assert estoque_apos == 3
        with allure.step("Cancelar compra e verificar restauracao do estoque"):
            cancelar_compra(base_url, token_admin)
            estoque_restaurado = buscar_produto(base_url, pid).json()["quantidade"]
            allure.attach(f"Estoque antes: 5 | Apos carrinho: 3 | Apos cancelar: {estoque_restaurado}", name="Estoque", attachment_type=allure.attachment_type.TEXT)
            assert estoque_restaurado == 5
        excluir_produto(base_url, token_admin, pid)

    @allure.story("Autenticacao")
    @allure.title("C15 - Criar carrinho sem token retorna 401 [M02]")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "seguranca")
    def test_criar_carrinho_sem_token_retorna_401(self, base_url, produto_criado):
        import requests as req
        with allure.step("POST /carrinhos sem Authorization header"):
            response = req.post(
                f"{base_url}/carrinhos",
                json={"produtos": [{"idProduto": produto_criado["id"], "quantidade": 1}]},
            )
        with allure.step("Validar 401"):
            assert response.status_code == 401
            assert "message" in response.json()