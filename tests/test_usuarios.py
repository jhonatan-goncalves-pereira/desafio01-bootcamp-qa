import allure
import jsonschema
from helpers.generators import gerar_usuario, gerar_email_unico
from helpers.usuarios_helper import (
    listar_usuarios, criar_usuario, buscar_usuario,
    atualizar_usuario, excluir_usuario,
)

USUARIO_SCHEMA = {
    "type": "object",
    "required": ["nome", "email", "password", "administrador", "_id"],
    "properties": {
        "_id": {"type": "string"},
        "nome": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "administrador": {"type": "string", "enum": ["true", "false"]},
    },
}
LISTA_USUARIOS_SCHEMA = {
    "type": "object",
    "required": ["quantidade", "usuarios"],
    "properties": {
        "quantidade": {"type": "integer"},
        "usuarios": {"type": "array", "items": USUARIO_SCHEMA},
    },
}


@allure.epic("ServeRest API")
@allure.feature("Usuarios")
class TestUsuarios:

    @allure.story("Listagem")
    @allure.title("U01 - GET /usuarios retorna 200 e schema valido")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_listar_usuarios_retorna_status_200(self, base_url):
        with allure.step("Chamar GET /usuarios"):
            response = listar_usuarios(base_url)
        with allure.step("Validar 200 e JSON Schema"):
            assert response.status_code == 200
            body = response.json()
            allure.attach(str(body)[:300], name="Response", attachment_type=allure.attachment_type.JSON)
            assert "usuarios" in body
            assert isinstance(body["usuarios"], list)
            jsonschema.validate(instance=body, schema=LISTA_USUARIOS_SCHEMA)

    @allure.story("Listagem")
    @allure.title("U02 - quantidade igual ao tamanho do array")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo", "contrato")
    def test_listar_usuarios_retorna_campo_quantidade(self, base_url):
        response = listar_usuarios(base_url)
        data = response.json()
        assert response.status_code == 200
        assert data["quantidade"] == len(data["usuarios"])

    @allure.story("Filtros")
    @allure.title("U03 - Filtro administrador=true retorna so admins")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo")
    def test_filtrar_usuarios_por_administrador_true(self, base_url):
        response = listar_usuarios(base_url, params={"administrador": "true"})
        assert response.status_code == 200
        for u in response.json()["usuarios"]:
            assert u["administrador"] == "true"

    @allure.story("Filtros")
    @allure.title("U04 - administrador=True maiusculo retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_filtrar_usuarios_administrador_case_sensitive(self, base_url):
        response = listar_usuarios(base_url, params={"administrador": "True"})
        assert response.status_code == 400

    @allure.story("Cadastro")
    @allure.title("U05 - Cadastrar usuario valido retorna 201 com _id")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_cadastrar_usuario_valido_retorna_201_com_id(self, base_url, usuario_payload):
        with allure.step("POST /usuarios payload valido"):
            response = criar_usuario(base_url, usuario_payload)
            data = response.json()
        with allure.step("Validar 201 e _id"):
            assert response.status_code == 201
            assert "_id" in data
            allure.attach(str(data), name="Criado", attachment_type=allure.attachment_type.JSON)
        excluir_usuario(base_url, data["_id"])

    @allure.story("Cadastro")
    @allure.title("U06 - Email duplicado retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_cadastrar_usuario_com_email_duplicado_retorna_400(self, base_url, usuario_criado):
        payload = {"nome": "Outro", "email": usuario_criado["email"], "password": "x", "administrador": "false"}
        response = criar_usuario(base_url, payload)
        assert response.status_code == 400
        assert "message" in response.json()

    @allure.story("Cadastro")
    @allure.title("U07 - Sem nome retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_cadastrar_usuario_sem_nome_retorna_400(self, base_url):
        response = criar_usuario(base_url, {"email": gerar_email_unico(), "password": "s", "administrador": "true"})
        assert response.status_code == 400

    @allure.story("Cadastro")
    @allure.title("U08 - Sem email retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_cadastrar_usuario_sem_email_retorna_400(self, base_url):
        response = criar_usuario(base_url, {"nome": "Sem Email", "password": "s", "administrador": "true"})
        assert response.status_code == 400

    @allure.story("Cadastro")
    @allure.title("U09 - Sem password retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_cadastrar_usuario_sem_password_retorna_400(self, base_url):
        response = criar_usuario(base_url, {"nome": "Sem Senha", "email": gerar_email_unico(), "administrador": "true"})
        assert response.status_code == 400

    @allure.story("Cadastro")
    @allure.title("U10 - Campo extra desconhecido retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo", "seguranca")
    def test_cadastrar_usuario_com_campo_extra_retorna_400(self, base_url):
        payload = {"nome": "H", "email": gerar_email_unico(), "password": "x", "administrador": "true", "injetado": "v"}
        response = criar_usuario(base_url, payload)
        assert response.status_code == 400

    @allure.story("Cadastro")
    @allure.title("U11 - administrador como booleano JSON retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo", "contrato")
    def test_cadastrar_usuario_administrador_como_booleano_retorna_400(self, base_url):
        import requests as req
        r = req.post(f"{base_url}/usuarios", json={"nome": "Bool", "email": gerar_email_unico(), "password": "x", "administrador": True})
        assert r.status_code == 400

    @allure.story("Seguranca")
    @allure.title("U12 - GET /usuarios/{id} expoe senha em plaintext [BUG CRITICO #2]")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("bug", "seguranca", "regressao")
    @allure.issue("2", "BUG #2 - Senhas em plaintext")
    def test_senha_exposta_em_texto_puro_no_get_por_id(self, base_url, usuario_criado):
        response = buscar_usuario(base_url, usuario_criado["id"])
        assert response.status_code == 200
        body = response.json()
        assert "password" in body
        assert body["password"] == usuario_criado["password"]

    @allure.story("Seguranca")
    @allure.title("U13 - GET /usuarios expoe senhas na listagem [BUG CRITICO #2]")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("bug", "seguranca", "regressao")
    @allure.issue("2", "BUG #2 - Senhas em plaintext")
    def test_senha_exposta_em_listagem_de_usuarios(self, base_url, usuario_criado):
        response = listar_usuarios(base_url, params={"email": usuario_criado["email"]})
        assert response.status_code == 200
        usuarios = response.json()["usuarios"]
        assert len(usuarios) == 1
        assert "password" in usuarios[0]
        assert usuarios[0]["password"] == usuario_criado["password"]

    @allure.story("Busca por ID")
    @allure.title("U14 - Buscar por ID valido retorna 200 e schema")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_buscar_usuario_por_id_valido_retorna_200(self, base_url, usuario_criado):
        response = buscar_usuario(base_url, usuario_criado["id"])
        data = response.json()
        assert response.status_code == 200
        assert data["_id"] == usuario_criado["id"]
        jsonschema.validate(instance=data, schema=USUARIO_SCHEMA)

    @allure.story("Busca por ID")
    @allure.title("U15 - ID inexistente retorna 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_buscar_usuario_por_id_inexistente_retorna_400(self, base_url):
        response = buscar_usuario(base_url, "aaaaaaaaaaaaaaaa")
        assert response.status_code == 400
        assert "message" in response.json()

    @allure.story("Busca por ID")
    @allure.title("U16 - ID formato invalido retorna 400 [BUG #1]")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negativo", "bug")
    @allure.issue("1", "BUG #1 - Contrato de erro inconsistente")
    def test_buscar_usuario_por_id_formato_invalido_retorna_400(self, base_url):
        response = buscar_usuario(base_url, "abc")
        assert response.status_code == 400
        assert "id" in response.json()

    @allure.story("Atualizacao")
    @allure.title("U17 - Atualizar existente retorna 200")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo")
    def test_atualizar_usuario_existente_retorna_200(self, base_url, usuario_criado):
        payload = {"nome": "Nome Atualizado QA", "email": gerar_email_unico(), "password": "nova456", "administrador": "false"}
        response = atualizar_usuario(base_url, usuario_criado["id"], payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Registro alterado com sucesso"

    @allure.story("Atualizacao")
    @allure.title("U18 - PUT em ID inexistente cria novo upsert 201")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("borda")
    def test_atualizar_usuario_com_id_inexistente_cria_novo(self, base_url):
        payload = gerar_usuario()
        response = atualizar_usuario(base_url, "id_que_nao_existe_abc123", payload)
        data = response.json()
        assert response.status_code == 201
        assert "_id" in data
        excluir_usuario(base_url, data["_id"])

    @allure.story("Exclusao")
    @allure.title("U19 - Excluir existente retorna 200")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo")
    def test_excluir_usuario_existente_retorna_200(self, base_url, usuario_criado):
        response = excluir_usuario(base_url, usuario_criado["id"])
        assert response.status_code == 200
        assert response.json()["message"] == "Registro exclu\u00eddo com sucesso"

    @allure.story("Exclusao")
    @allure.title("U20 - Excluir ID inexistente retorna 200 sem registro")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("borda")
    def test_excluir_usuario_id_inexistente_retorna_200_sem_registro(self, base_url):
        response = excluir_usuario(base_url, "id_que_nao_existe_para_delete")
        assert response.status_code == 200
        assert "Nenhum registro exclu\u00eddo" in response.json()["message"]

    @allure.story("Exclusao")
    @allure.title("U21 - Excluir usuario com carrinho ativo retorna 400 [M05]")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "integridade")
    def test_excluir_usuario_com_carrinho_ativo_retorna_400(self, base_url, usuario_criado, token_admin, produto_criado):
        from helpers.carrinho_helper import criar_carrinho, cancelar_compra
        with allure.step("Criar carrinho para o usuario"):
            r = criar_carrinho(base_url, token_admin, produto_criado["id"])
            assert r.status_code == 201
        with allure.step("Tentar excluir usuario com carrinho ativo"):
            response = excluir_usuario(base_url, usuario_criado["id"])
        cancelar_compra(base_url, token_admin)
        with allure.step("Validar 400"):
            assert response.status_code == 400
            assert "message" in response.json()
