import pytest
import requests
from helpers.generators import gerar_usuario, gerar_email_unico

BASE_URL = "https://compassuol.serverest.dev"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def usuario_payload():
    return gerar_usuario()


@pytest.fixture
def usuario_criado(base_url, usuario_payload):
    response = requests.post(f"{base_url}/usuarios", json=usuario_payload)
    assert response.status_code == 201, f"Falha ao criar usuário no setup: {response.json()}"
    user_id = response.json()["_id"]

    yield {
        "id": user_id,
        **usuario_payload
    }

    requests.delete(f"{base_url}/usuarios/{user_id}")
