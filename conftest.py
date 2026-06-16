import pytest
import requests
from helpers.login_helper import realizar_login
from helpers.generators import gerar_produto
from helpers.produtos_helper import criar_produto, excluir_produto

BASE_URL = "https://compassuol.serverest.dev"
HTTP_TIMEOUT = 15  # segundos

ADMIN_EMAIL    = "fulano@qa.com"
ADMIN_PASSWORD = "teste"
ADMIN_NOME     = "Fulano da Silva"

_admin_state = {"id": "mjOe8noXEoYaf3A4"}



def _get_current_admin_id(base_url: str) -> str:
    try:
        r = requests.get(
            f"{base_url}/usuarios",
            params={"email": ADMIN_EMAIL},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200 and r.json()["quantidade"] > 0:
            current_id = r.json()["usuarios"][0]["_id"]
            _admin_state["id"] = current_id  # manter sincronizado
            return current_id
    except Exception:
        pass
    return _admin_state["id"]


def _login_admin(base_url: str) -> str:
    response = realizar_login(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert response.status_code == 200, (
        f"Falha ao autenticar admin: {response.status_code} {response.text}"
    )
    return response.json()["authorization"]


def _restaurar_fulano(base_url: str, token: str) -> None:
    payload = {
        "nome": ADMIN_NOME,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "administrador": "true",
    }
    try:
        r = requests.put(
            f"{base_url}/usuarios/{_get_current_admin_id(base_url)}",
            json=payload,
            headers={"Authorization": token},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200:
            return 
    except Exception:
        pass

    try:
        r_post = requests.post(
            f"{base_url}/usuarios",
            json=payload,
            timeout=HTTP_TIMEOUT,
        )
        if r_post.status_code == 201:
            _admin_state["id"] = r_post.json()["_id"]
        elif r_post.status_code == 400:
            r_list = requests.get(
                f"{base_url}/usuarios",
                params={"email": ADMIN_EMAIL},
                timeout=HTTP_TIMEOUT,
            )
            if r_list.status_code == 200 and r_list.json()["quantidade"] > 0:
                _admin_state["id"] = r_list.json()["usuarios"][0]["_id"]
    except Exception:
        pass


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def usuario_payload():
    import uuid
    return {
        "nome": "Usuário QA Automatizando",
        "email": f"qa_{uuid.uuid4().hex[:10]}@qa.com",
        "password": "teste@123",
        "administrador": "true",
    }


@pytest.fixture
def usuario_criado(base_url):
    _restaurar_fulano(base_url, _login_admin(base_url))

    token_pre = _login_admin(base_url)

    yield {
        "id": _get_current_admin_id(base_url),
        "nome": ADMIN_NOME,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "administrador": "true",
    }

    try:
        requests.delete(
            f"{base_url}/carrinhos/cancelar-compra",
            headers={"Authorization": token_pre},
            timeout=HTTP_TIMEOUT,
        )
    except Exception:
        pass

    _restaurar_fulano(base_url, token_pre)


@pytest.fixture(scope="session")
def token_admin(base_url):
    return _login_admin(base_url)


@pytest.fixture
def token_nao_admin(base_url):
    token_original = _login_admin(base_url)

    r_put = requests.put(
        f"{base_url}/usuarios/{_get_current_admin_id(base_url)}",
        json={
            "nome": ADMIN_NOME,
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "administrador": "false",
        },
        headers={"Authorization": token_original},
        timeout=HTTP_TIMEOUT,
    )
    assert r_put.status_code == 200, f"Falha ao rebaixar admin: {r_put.text}"

    response = realizar_login(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    if response.status_code != 200:
        _restaurar_fulano(base_url, token_original)
        pytest.fail(
            f"Falha ao obter token não-admin: {response.status_code} {response.text}"
        )
    token = response.json()["authorization"]

    yield token

    try:
        _restaurar_fulano(base_url, token)
    except Exception:
        pass


@pytest.fixture
def produto_criado(base_url, token_admin):
    payload = gerar_produto()
    response = criar_produto(base_url, token_admin, payload)
    assert response.status_code == 201, (
        f"Falha ao criar produto no setup: {response.json()}"
    )
    produto_id = response.json()["_id"]
    yield {"id": produto_id, **payload}
    try:
        excluir_produto(base_url, token_admin, produto_id)
    except Exception:
        pass
