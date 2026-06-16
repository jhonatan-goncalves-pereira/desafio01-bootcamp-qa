"""
conftest.py — fixtures globais do projeto ServeRest (compassuol.serverest.dev)

LIMITAÇÃO CONHECIDA DA INSTÂNCIA:
  O endpoint POST /login é instável — trava ou retorna timeout esporadicamente,
  especialmente para chamadas consecutivas em curto intervalo. Apenas o usuário
  pré-existente fulano@qa.com autentica com sucesso nesta instância.

  Estratégia adotada:
  - token_admin     → scope="function" + retry com backoff (garante token fresco
                      após qualquer teste que altere o estado do fulano)
  - token_nao_admin → rebaixa fulano para não-admin → login → yield token
                      → restaura como admin no teardown
  - usuario_criado  → retorna fulano@qa.com (único usuário persistido e
                      autenticável); teardown restaura estado original
  - produto_criado  → cria produto com token_admin fresco; teardown limpa
"""

import time
import pytest
import requests
from helpers.login_helper import realizar_login
from helpers.generators import gerar_produto
from helpers.produtos_helper import criar_produto, excluir_produto

BASE_URL       = "https://compassuol.serverest.dev"
HTTP_TIMEOUT   = 15   # segundos para chamadas gerais
LOGIN_RETRIES  = 3    # tentativas de login antes de desistir
LOGIN_BACKOFF  = 3    # segundos entre tentativas

ADMIN_EMAIL    = "fulano@qa.com"
ADMIN_PASSWORD = "teste"
ADMIN_NOME     = "Fulano da Silva"

# ID mutável — atualizado sempre que o fulano é recriado
_admin_state = {"id": "mjOe8noXEoYaf3A4"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _login_com_retry(base_url: str, email: str, password: str) -> str:
    """Faz login com retry e backoff exponencial.

    Retorna o token Bearer ou levanta AssertionError após todas as tentativas.
    Necessário porque o /login da instância compassuol é instável sob carga
    paralela ou após chamadas consecutivas.
    """
    last_exc = None
    for attempt in range(1, LOGIN_RETRIES + 1):
        try:
            response = realizar_login(base_url, email, password)
            if response.status_code == 200:
                return response.json()["authorization"]
            # 401 não é problema de rede — falha imediata
            if response.status_code == 401:
                raise AssertionError(
                    f"Credenciais inválidas para {email}: {response.json()}"
                )
        except AssertionError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < LOGIN_RETRIES:
                time.sleep(LOGIN_BACKOFF * attempt)

    raise AssertionError(
        f"Login falhou após {LOGIN_RETRIES} tentativas. Último erro: {last_exc}"
    )


def _get_current_admin_id(base_url: str) -> str:
    """Retorna o ID atual do fulano buscando na API (resiliente a recriações)."""
    try:
        r = requests.get(
            f"{base_url}/usuarios",
            params={"email": ADMIN_EMAIL},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200 and r.json()["quantidade"] > 0:
            current_id = r.json()["usuarios"][0]["_id"]
            _admin_state["id"] = current_id
            return current_id
    except Exception:
        pass
    return _admin_state["id"]


def _restaurar_fulano(base_url: str, token: str) -> None:
    """Restaura o fulano ao estado admin original.

    1. Tenta PUT com o token fornecido.
    2. Se falhar (fulano foi deletado), recria via POST e atualiza o ID.
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
            return
    except Exception:
        pass

    # Fulano provavelmente foi deletado — recriar
    try:
        r_post = requests.post(
            f"{base_url}/usuarios",
            json=payload,
            timeout=HTTP_TIMEOUT,
        )
        if r_post.status_code == 201:
            _admin_state["id"] = r_post.json()["_id"]
            return
        if r_post.status_code == 400:
            # Email já em uso por outro ID (recriado por outro teardown)
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

    Garante estado correto antes do teste e restaura após — inclusive se o
    teste excluir ou alterar o fulano. Usa apenas UM login no setup (o token
    capturado antes do yield) para evitar múltiplos hits no /login instável.
    """
    # 1 login: obtém token e já garante estado admin
    token_pre = _login_com_retry(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    _restaurar_fulano(base_url, token_pre)
    # Rebuscar token após possível restauração (estado pode ter mudado)
    token_pre = _login_com_retry(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)

    yield {
        "id": _get_current_admin_id(base_url),
        "nome": ADMIN_NOME,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "administrador": "true",
    }

    # Teardown: cancelar carrinho ativo (se existir) e restaurar fulano
    try:
        requests.delete(
            f"{base_url}/carrinhos/cancelar-compra",
            headers={"Authorization": token_pre},
            timeout=HTTP_TIMEOUT,
        )
    except Exception:
        pass

    _restaurar_fulano(base_url, token_pre)


@pytest.fixture
def token_admin(base_url):
    """Token Bearer do administrador — obtido a cada teste (scope=function).

    scope="function" é necessário porque token_nao_admin altera o estado
    do fulano entre testes. Um token de sessão ficaria desatualizado (403)
    após o teste de não-admin rebaixar e restaurar o fulano.
    """
    return _login_com_retry(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def token_nao_admin(base_url):
    """Token de usuário não-admin via rebaixamento temporário do fulano.

    Fluxo: login admin → rebaixa fulano → login não-admin → yield
    → restaura admin no teardown com token pré-yield.
    """
    # Obter token admin antes de qualquer alteração
    token_admin_atual = _login_com_retry(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)

    # Rebaixar para não-admin
    r_put = requests.put(
        f"{base_url}/usuarios/{_get_current_admin_id(base_url)}",
        json={
            "nome": ADMIN_NOME,
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "administrador": "false",
        },
        headers={"Authorization": token_admin_atual},
        timeout=HTTP_TIMEOUT,
    )
    assert r_put.status_code == 200, (
        f"Falha ao rebaixar admin para não-admin: {r_put.status_code} {r_put.text}"
    )

    # Login com fulano agora como não-admin
    token_nao_admin = _login_com_retry(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)

    yield token_nao_admin

    # Teardown: restaurar como admin usando o token não-admin
    # (PUT não exige ser admin, apenas estar autenticado)
    _restaurar_fulano(base_url, token_nao_admin)


@pytest.fixture
def produto_criado(base_url, token_admin):
    """Cria produto com token admin fresco e remove no teardown."""
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
