import allure
import jsonschema
import pytest
from helpers.login_helper import realizar_login
from helpers.generators import gerar_email_unico


LOGIN_SUCESSO_SCHEMA = {
    "type": "object",
    "required": ["message", "authorization"],
    "properties": {
        "message": {"type": "string"},
        "authorization": {"type": "string"},
    },
    "additionalProperties": False,
}


@allure.epic("ServeRest API")
@allure.feature("Autenticacao")
class TestLogin:

    @allure.story("Login com sucesso")
    @allure.title("L01 - Credenciais validas retornam 200 e token Bearer JWT")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positivo", "smoke")
    def test_login_com_sucesso_retorna_200_e_token(self, base_url, usuario_criado):
        with allure.step("Enviar POST /login com credenciais validas"):
            response = realizar_login(base_url, usuario_criado["email"], usuario_criado["password"])

        with allure.step("Validar status 200 e presenca do token"):
            assert response.status_code == 200
            body = response.json()
            allure.attach(str(body), name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert body["message"] == "Login realizado com sucesso"
            assert "authorization" in body
            assert body["authorization"].startswith("Bearer ")

        with allure.step("Validar JSON Schema da resposta"):
            jsonschema.validate(instance=body, schema=LOGIN_SUCESSO_SCHEMA)

    @allure.story("Login com sucesso")
    @allure.title("L02 - Token retornado tem formato Bearer JWT valido (3 partes)")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positivo", "contrato")
    def test_token_retornado_tem_formato_bearer_jwt(self, base_url, usuario_criado):
        with allure.step("Realizar login e capturar token"):
            response = realizar_login(base_url, usuario_criado["email"], usuario_criado["password"])
            assert response.status_code == 200
            token = response.json()["authorization"]

        with allure.step("Verificar que o token tem 3 partes separadas por ponto"):
            partes = token.replace("Bearer ", "").split(".")
            allure.attach(token, name="Token JWT", attachment_type=allure.attachment_type.TEXT)
            assert len(partes) == 3, f"Token nao e um JWT valido: {token}"

    @allure.story("Login com falha")
    @allure.title("L03 - Senha incorreta retorna 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo", "seguranca")
    def test_login_com_senha_incorreta_retorna_401(self, base_url, usuario_criado):
        with allure.step("Enviar POST /login com senha errada"):
            response = realizar_login(base_url, usuario_criado["email"], "senha_errada_xpto_999")

        with allure.step("Validar status 401 e campo message"):
            assert response.status_code == 401
            body = response.json()
            allure.attach(str(body), name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert "message" in body

    @allure.story("Login com falha")
    @allure.title("L04 - Email inexistente retorna 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negativo")
    def test_login_com_email_inexistente_retorna_401(self, base_url):
        with allure.step("Enviar POST /login com email que nao existe"):
            response = realizar_login(base_url, gerar_email_unico(), "qualquer_senha")

        with allure.step("Validar status 401"):
            assert response.status_code == 401
            assert "message" in response.json()

    @allure.story("Validacao de campos obrigatorios")
    @allure.title("L05 - Email vazio retorna 400 [BUG #1]")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo", "bug")
    @allure.issue("1", "BUG #1 - Contrato de erro inconsistente")
    def test_login_sem_email_retorna_400(self, base_url):
        """BUG #1: A API retorna {email: ...} em vez de {message: ...}."""
        with allure.step("Enviar POST /login com email em branco"):
            response = realizar_login(base_url, "", "senha123")

        with allure.step("Validar status 400 e chave email na resposta"):
            assert response.status_code == 400
            body = response.json()
            allure.attach(str(body), name="Response Body (BUG #1)", attachment_type=allure.attachment_type.JSON)
            assert "email" in body

    @allure.story("Validacao de campos obrigatorios")
    @allure.title("L06 - Password vazio retorna 400 [BUG #1]")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo", "bug")
    @allure.issue("1", "BUG #1 - Contrato de erro inconsistente")
    def test_login_sem_password_retorna_400(self, base_url):
        """BUG #1: A API retorna {password: ...} em vez de {message: ...}."""
        with allure.step("Enviar POST /login com password em branco"):
            response = realizar_login(base_url, gerar_email_unico(), "")

        with allure.step("Validar status 400 e chave password na resposta"):
            assert response.status_code == 400
            body = response.json()
            allure.attach(str(body), name="Response Body (BUG #1)", attachment_type=allure.attachment_type.JSON)
            assert "password" in body

    @allure.story("Validacao de campos obrigatorios")
    @allure.title("L07 - Ambos os campos vazios retornam 400")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negativo")
    def test_login_sem_ambos_campos_retorna_400(self, base_url):
        with allure.step("Enviar POST /login com email e password em branco"):
            response = realizar_login(base_url, "", "")

        with allure.step("Validar status 400"):
            assert response.status_code == 400
