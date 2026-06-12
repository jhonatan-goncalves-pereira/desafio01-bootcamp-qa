import requests
from helpers.generators import gerar_usuario, gerar_email_unico

def test_listar_usuarios_retorna_status_200(base_url):
    url = f"{base_url}/usuarios"
    response = requests.get(url)

    assert response.status_code == 200
    assert "usuarios" in response.json()
    assert isinstance(response.json()["usuarios"], list)

def test_listar_usuarios_retorna_campo_quantidade(base_url):
    url = f"{base_url}/usuarios"
    response = requests.get(url)
    data = response.json()

    assert response.status_code == 200
    assert "quantidade" in data
    assert isinstance(data["quantidade"], int)


def test_cadastrar_usuario_valido_retorna_201_com_id(base_url, usuario_payload):
    url = f"{base_url}/usuarios"
    response = requests.post(url, json=usuario_payload)
    data = response.json()

    assert response.status_code == 201
    assert "_id" in data
    assert isinstance(data["_id"], str)
    requests.delete(f"{base_url}/usuarios/{data['_id']}")


def test_cadastrar_usuario_com_email_duplicado_retorna_400(base_url, usuario_criado):
    url = f"{base_url}/usuarios"
    payload_duplicado = {
        "nome": "Outro Nome",
        "email": usuario_criado["email"],
        "password": "outrasenha",
        "administrador": "false"
    }
    response = requests.post(url, json=payload_duplicado)

    assert response.status_code == 400


def test_cadastrar_usuario_sem_nome_retorna_400(base_url):
    url = f"{base_url}/usuarios"
    payload_incompleto = {
        "email": gerar_email_unico(),
        "password": "senha123",
        "administrador": "true"
    }
    response = requests.post(url, json=payload_incompleto)
    assert response.status_code == 400


def test_cadastrar_usuario_sem_email_retorna_400(base_url):
    url = f"{base_url}/usuarios"
    payload_incompleto = {
        "nome": "Fulano sem email",
        "password": "senha123",
        "administrador": "true"
    }
    response = requests.post(url, json=payload_incompleto)
    assert response.status_code == 400


def test_cadastrar_usuario_sem_password_retorna_400(base_url):
    url = f"{base_url}/usuarios"
    payload_incompleto = {
        "nome": "Fulano sem senha",
        "email": gerar_email_unico(),
        "administrador": "true"
    }
    response = requests.post(url, json=payload_incompleto)
    assert response.status_code == 400, "Payload sem 'password' deveria retornar 400"
