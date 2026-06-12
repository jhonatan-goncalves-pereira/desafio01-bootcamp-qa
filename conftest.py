import pytest
import requests
from helpers.login_helper import realizar_login
from helpers.generators import gerar_usuario
from helpers.generators import gerar_produto
from helpers.produtos_helper import criar_produto

BASE_URL = "https://compassuol.serverest.dev"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture
def token_admin(base_url, usuario_criado):
    response = realizar_login(
        base_url,
        usuario_criado["email"],
        usuario_criado["password"]
    )
    assert response.status_code == 200
    return response.json()["authorization"]

@pytest.fixture
def usuario_payload():
    return gerar_usuario()


@pytest.fixture
def usuario_criado(base_url, usuario_payload):
    response = requests.post(
        f"{base_url}/usuarios",
        json=usuario_payload
    )
    assert response.status_code == 201, (
        f"Falha ao criar usuário no setup: {response.json()}"
    )
    user_id = response.json()["_id"]
    yield {
        "id": user_id,
        **usuario_payload
    }
    requests.delete(f"{base_url}/usuarios/{user_id}")
    
@pytest.fixture
def produto_criado(base_url, token_admin):
    payload = gerar_produto()
    response = criar_produto(
        base_url,
        token_admin,
        payload
    )
    assert response.status_code == 201
    produto_id = response.json()["_id"]
    return {
        "id": produto_id,
        **payload
    }