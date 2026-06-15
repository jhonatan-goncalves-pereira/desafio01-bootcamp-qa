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

# cenários positivos 01 ao 02
def test_login_com_sucesso_retorna_200_e_token(base_url, usuario_criado):
    response = realizar_login(base_url, usuario_criado["email"], usuario_criado["password"])
    
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Login realizado com sucesso"
    assert "authorization" in body
    assert body["authorization"].startswith("Bearer ")
    jsonschema.validate(instance=body, schema=LOGIN_SUCESSO_SCHEMA)

def test_token_retornado_tem_formato_bearer_jwt(base_url, usuario_criado):
    response = realizar_login(base_url, usuario_criado["email"], usuario_criado["password"])
    
    assert response.status_code == 200
    token = response.json()["authorization"]
    partes = token.replace("Bearer ", "").split(".")
    assert len(partes) == 3, f"Token não é um JWT válido: {token}"


# cenários negativos 03 ao 07
def test_login_com_senha_incorreta_retorna_401(base_url, usuario_criado):
    response = realizar_login(base_url, usuario_criado["email"], "senha_errada_xpto_999")

    assert response.status_code == 401
    body = response.json()
    assert "message" in body

def test_login_com_email_inexistente_retorna_401(base_url):
    response = realizar_login(base_url, gerar_email_unico(), "qualquer_senha")

    assert response.status_code == 401
    assert "message" in response.json()


def test_login_sem_email_retorna_400(base_url):
    """Bug 01 - E-mail vazio retorna 400.
    BUG DOCUMENTADO: A API retorna {'email': '...'} em vez de {'message': '...'},
    quebrando a consistência do contrato de erro. Ver Issue #1.
    """
    response = realizar_login(base_url, "", "senha123")

    assert response.status_code == 400
    body = response.json()
    assert "email" in body


def test_login_sem_password_retorna_400(base_url):
    """Bug 02 - password vazio retorna 400.
    BUG DOCUMENTADO: A API retorna {'password': '...'} em vez de {'message': '...'},
    quebrando a consistência do contrato de erro. Ver Issue #1.
    """
    response = realizar_login(base_url, gerar_email_unico(), "")

    assert response.status_code == 400
    body = response.json()
    assert "password" in body


def test_login_sem_ambos_campos_retorna_400(base_url):
    response = realizar_login(base_url, "", "")

    assert response.status_code == 400
