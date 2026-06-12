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

