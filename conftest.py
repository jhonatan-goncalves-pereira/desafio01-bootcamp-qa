"""
conftest.py — fixtures globais do projeto ServeRest (compassuol.serverest.dev)

LIMITAÇÃO CONHECIDA DA INSTÂNCIA:
  O endpoint POST /login trava para usuários criados dinamicamente.
  Apenas o usuário pré-existente fulano@qa.com autentica com sucesso.

  Estratégia:
  - usuario_criado  → usa o fulano@qa.com como usuário de teste real.
                      Teardown restaura o fulano ao estado original.
                      Se deletado pelo teste, recria via POST e atualiza o ID.
  - token_admin     → login com fulano@qa.com (scope=session)
  - token_nao_admin → rebaixa fulano para não-admin → captura token
                      → restaura como admin no teardown
"""

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

# Estado mutável: o ID do fulano pode mudar se ele for recriado após exclusão
_admin_state = {"id": "mjOe8noXEoYaf3A4"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_current_admin_id(base_url: str) -> str:
    """Busca o ID atual do fulano@qa.com na API (pode mudar após recriação)."""
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
    """Login com fulano@qa.com. Levanta AssertionError se falhar."""
    response = realizar_login(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert response.status_code == 200, (
        f"Falha ao autenticar admin: {response.status_code} {response.text}"
    )
    return response.json()["authorization"]


def _restaurar_fulano(base_url: str, token: str) -> None:
    """Restaura o fulano ao estado original usando o token fornecido.

    Se o PUT falhar (fulano foi deletado), recria via POST e atualiza o ID.
    """
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
            return  # Restaurado com sucesso
    except Exception:
        pass

    # PUT falhou — o fulano foi deletado ou o ID não existe mais.
    # Recriar via POST e atualizar o ID global.
    try:
        r_post = requests.post(
            f"{base_url}/usuarios",
            json=payload,
            timeout=HTTP_TIMEOUT,
        )
        if r_post.status_code == 201:
            _admin_state["id"] = r_post.json()["_id"]
        # Se retornar 400 "email já em uso", outro fulano já foi criado;
        # buscar pelo email e atualizar o ID
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


# ── Fixtures ──────────────────────────────────────────────────────────────────

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
    """Retorna o fulano@qa.com como usuário de teste.

    Captura o token ANTES do yield (antes que o teste possa alterar
    email/senha), e usa-o no teardown para restaurar o estado original.
    Isso garante que mesmo testes que alterem ou excluam o fulano não
    corrompam os testes subsequentes.
    """
    # Garantir que o fulano está no estado correto antes de começar
    _restaurar_fulano(base_url, _login_admin(base_url))

    # Capturar token ANTES do teste (credenciais ainda são as originais)
    token_pre = _login_admin(base_url)

    yield {
        "id": _get_current_admin_id(base_url),
        "nome": ADMIN_NOME,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "administrador": "true",
    }

    # Teardown: cancelar carrinho se existir, depois restaurar fulano
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
    """Token Bearer do admin (obtido uma única vez por sessão)."""
    return _login_admin(base_url)


@pytest.fixture
def token_nao_admin(base_url):
    """Token de usuário não-admin via rebaixamento temporário do fulano."""
    token_original = _login_admin(base_url)

    # Rebaixar fulano para não-admin
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

    # Login com fulano agora como não-admin
    response = realizar_login(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    if response.status_code != 200:
        # Restaurar antes de falhar
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
