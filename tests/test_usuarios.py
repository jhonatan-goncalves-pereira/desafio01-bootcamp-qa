import jsonschema
from helpers.generators import gerar_usuario, gerar_email_unico
from helpers.usuarios_helper import (
    listar_usuarios,
    criar_usuario,
    buscar_usuario,
    atualizar_usuario,
    excluir_usuario,
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
        "usuarios": {
            "type": "array",
            "items": USUARIO_SCHEMA,
        },
    },
}

# cenários de testes u01 ao u16
def test_listar_usuarios_retorna_status_200(base_url):
    response = listar_usuarios(base_url)

    assert response.status_code == 200
    body = response.json()
    assert "usuarios" in body
    assert isinstance(body["usuarios"], list)
    jsonschema.validate(instance=body, schema=LISTA_USUARIOS_SCHEMA)


def test_listar_usuarios_retorna_campo_quantidade(base_url):
    response = listar_usuarios(base_url)
    data = response.json()

    assert response.status_code == 200
    assert "quantidade" in data
    assert isinstance(data["quantidade"], int)
    assert data["quantidade"] == len(data["usuarios"])


def test_filtrar_usuarios_por_administrador_true(base_url):
    response = listar_usuarios(base_url, params={"administrador": "true"})

    assert response.status_code == 200
    body = response.json()
    for usuario in body["usuarios"]:
        assert usuario["administrador"] == "true"


def test_filtrar_usuarios_administrador_case_sensitive(base_url):
    """ isue retorno
    u04 — Filtro ?administrador=True (maiúsculo) retorna 400.

    a api é case-sensitive no valor do filtro: aceita 'true'/'false' mas
    rejeita 'True', 'TRUE', 'False' etc.
    """
    response = listar_usuarios(base_url, params={"administrador": "True"})

    assert response.status_code == 400

def test_cadastrar_usuario_valido_retorna_201_com_id(base_url, usuario_payload):
    response = criar_usuario(base_url, usuario_payload)
    data = response.json()

    assert response.status_code == 201
    assert "_id" in data
    assert isinstance(data["_id"], str)

    excluir_usuario(base_url, data["_id"])

def test_cadastrar_usuario_com_email_duplicado_retorna_400(base_url, usuario_criado):
    payload_duplicado = {
        "nome": "Outro Nome",
        "email": usuario_criado["email"],
        "password": "outrasenha",
        "administrador": "false",
    }
    response = criar_usuario(base_url, payload_duplicado)

    assert response.status_code == 400
    assert "message" in response.json()


def test_cadastrar_usuario_sem_nome_retorna_400(base_url):
    payload = {"email": gerar_email_unico(), "password": "senha123", "administrador": "true"}
    response = criar_usuario(base_url, payload)

    assert response.status_code == 400


def test_cadastrar_usuario_sem_email_retorna_400(base_url):
    payload = {"nome": "Sem Email", "password": "senha123", "administrador": "true"}
    response = criar_usuario(base_url, payload)

    assert response.status_code == 400


def test_cadastrar_usuario_sem_password_retorna_400(base_url):
    payload = {"nome": "Sem Senha", "email": gerar_email_unico(), "administrador": "true"}
    response = criar_usuario(base_url, payload)

    assert response.status_code == 400


def test_cadastrar_usuario_com_campo_extra_retorna_400(base_url):
    payload = {
        "nome": "Usuario Hacker",
        "email": gerar_email_unico(),
        "password": "senha123",
        "administrador": "true",
        "campo_injetado": "valor_malicioso",
    }
    response = criar_usuario(base_url, payload)

    assert response.status_code == 400


def test_cadastrar_usuario_administrador_como_booleano_retorna_400(base_url):
    """
    issue 02 - exigencia de entrada de dado

    A API exige a string 'true' ou 'false', não o tipo booleano JSON.
    """
    import requests as req
    r = req.post(
        f"{base_url}/usuarios",
        json={
            "nome": "Teste Booleano",
            "email": gerar_email_unico(),
            "password": "123",
            "administrador": True,
        },
    )
    assert r.status_code == 400


# BUG CRÍTICO: senhas em texto puro 

def test_senha_exposta_em_texto_puro_no_get_por_id(base_url, usuario_criado):
    """U12 — [BUG CRÍTICO #2] GET /usuarios/{id} expõe a senha em texto puro.

    A API retorna o campo 'password' com o valor em plaintext na resposta.
    Senhas jamais devem ser retornadas em respostas de API — deveriam ser
    omitidas ou exibidas como hash. Ver Issue #2.
    """
    response = buscar_usuario(base_url, usuario_criado["id"])

    assert response.status_code == 200
    body = response.json()
    # campo password está presente: BUG
    assert "password" in body
    assert body["password"] == usuario_criado["password"], (
        "BUG CONFIRMADO: senha retornada em texto puro"
    )


def test_senha_exposta_em_listagem_de_usuarios(base_url, usuario_criado):
    """U13 — [BUG CRÍTICO #2] GET /usuarios expõe senhas em texto puro na listagem.

    Todos os usuários retornados na listagem têm o campo 'password' visível.
    Ver Issue #2.
    """
    response = listar_usuarios(base_url, params={"email": usuario_criado["email"]})

    assert response.status_code == 200
    usuarios = response.json()["usuarios"]
    assert len(usuarios) == 1
    
    assert "password" in usuarios[0]
    assert usuarios[0]["password"] == usuario_criado["password"], (
        "BUG CONFIRMADO: senha retornada em texto puro na listagem"
    )



def test_buscar_usuario_por_id_valido_retorna_200(base_url, usuario_criado):
    response = buscar_usuario(base_url, usuario_criado["id"])
    data = response.json()

    assert response.status_code == 200
    assert data["_id"] == usuario_criado["id"]
    assert data["email"] == usuario_criado["email"]
    assert data["nome"] == usuario_criado["nome"]
    jsonschema.validate(instance=data, schema=USUARIO_SCHEMA)


def test_buscar_usuario_por_id_inexistente_retorna_400(base_url):
    response = buscar_usuario(base_url, "aaaaaaaaaaaaaaaa")

    assert response.status_code == 400
    assert "message" in response.json()


def test_buscar_usuario_por_id_formato_invalido_retorna_400(base_url):
    """U16 — GET /usuarios/{id} com ID curto (formato inválido) retorna 400.

    BUG DOCUMENTADO (Issue #1): retorna {'id': '...'} em vez de {'message': '...'}
    """
    response = buscar_usuario(base_url, "abc")

    assert response.status_code == 400
    body = response.json()
    
    assert "id" in body


# ── Atualização ────────────────────────────────────────────────────────────────


def test_atualizar_usuario_existente_retorna_200(base_url, usuario_criado):
    """U17 — PUT em usuário existente retorna 200."""
    payload_atualizado = {
        "nome": "Nome Atualizado QA",
        "email": gerar_email_unico(),
        "password": "novasenha456",
        "administrador": "false",
    }
    response = atualizar_usuario(base_url, usuario_criado["id"], payload_atualizado)

    assert response.status_code == 200
    assert response.json()["message"] == "Registro alterado com sucesso"


def test_atualizar_usuario_com_id_inexistente_cria_novo(base_url):
    """U18 — PUT em ID inexistente cria o usuário (retorna 201)."""
    payload = gerar_usuario()
    response = atualizar_usuario(base_url, "id_que_nao_existe_abc123", payload)
    data = response.json()

    assert response.status_code == 201
    assert "_id" in data

    excluir_usuario(base_url, data["_id"])




def test_excluir_usuario_existente_retorna_200(base_url, usuario_criado):
    response = excluir_usuario(base_url, usuario_criado["id"])

    assert response.status_code == 200
    assert response.json()["message"] == "Registro excluído com sucesso"


def test_excluir_usuario_id_inexistente_retorna_200_sem_registro(base_url):
    response = excluir_usuario(base_url, "id_que_nao_existe_para_delete")

    assert response.status_code == 200
    assert "Nenhum registro excluído" in response.json()["message"]


def test_excluir_usuario_com_carrinho_ativo_retorna_400(base_url, usuario_criado, token_admin, produto_criado):
    """U21 — [M05] DELETE /usuarios/{id} com carrinho ativo retorna 400.

    A API deve impedir a exclusão de um usuário que possui carrinho ativo,
    pois os dados do carrinho ficariam órfãos. O endpoint deve retornar 400
    com mensagem explicativa ao invés de excluir o registro.
    """
    from helpers.carrinho_helper import criar_carrinho, cancelar_compra

    # Criar carrinho para o usuário admin
    r_carrinho = criar_carrinho(base_url, token_admin, produto_criado["id"])
    assert r_carrinho.status_code == 201, (
        f"Setup falhou ao criar carrinho: {r_carrinho.json()}"
    )

    # Tentar excluir o usuário enquanto tem carrinho ativo
    response = excluir_usuario(base_url, usuario_criado["id"])

    # Teardown: limpar o carrinho independente do resultado
    cancelar_compra(base_url, token_admin)

    assert response.status_code == 400
    body = response.json()
    assert "message" in body
