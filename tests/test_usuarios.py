from helpers.generators import (gerar_usuario,gerar_email_unico)
from helpers.usuarios_helper import (listar_usuarios,criar_usuario,buscar_usuario,atualizar_usuario,excluir_usuario)

def test_listar_usuarios_retorna_status_200(base_url):
    response = listar_usuarios(base_url)
    assert response.status_code == 200
    assert "usuarios" in response.json()
    assert isinstance(response.json()["usuarios"], list)

def test_listar_usuarios_retorna_campo_quantidade(base_url):
    response = listar_usuarios(base_url)
    data = response.json()
    assert response.status_code == 200
    assert "quantidade" in data
    assert isinstance(data["quantidade"], int)

def test_cadastrar_usuario_valido_retorna_201_com_id(base_url,usuario_payload):
    response = criar_usuario(base_url,usuario_payload)
    data = response.json()
    assert response.status_code == 201
    assert "_id" in data
    assert isinstance(data["_id"], str)
    excluir_usuario(base_url,data["_id"])

def test_cadastrar_usuario_com_email_duplicado_retorna_400(base_url,usuario_criado):
    payload_duplicado = {
        "nome": "Outro Nome",
        "email": usuario_criado["email"],
        "password": "outrasenha",
        "administrador": "false"
    }
    response = criar_usuario(base_url,payload_duplicado)
    assert response.status_code == 400

def test_cadastrar_usuario_sem_nome_retorna_400(base_url):
    payload_incompleto = {
        "email": gerar_email_unico(),
        "password": "senha123",
        "administrador": "true"
    }
    response = criar_usuario(base_url,payload_incompleto)
    assert response.status_code == 400

def test_cadastrar_usuario_sem_email_retorna_400(base_url):
    payload_incompleto = {
        "nome": "Fulano sem email",
        "password": "senha123",
        "administrador": "true"
    }
    response = criar_usuario(base_url,payload_incompleto)
    assert response.status_code == 400

def test_cadastrar_usuario_sem_password_retorna_400(base_url):
    payload_incompleto = {
        "nome": "Fulano sem senha",
        "email": gerar_email_unico(),
        "administrador": "true"
    }
    response = criar_usuario(base_url,payload_incompleto)
    assert response.status_code == 400

def test_buscar_usuario_por_id_valido_retorna_200(base_url,usuario_criado):
    response = buscar_usuario(base_url,usuario_criado["id"])
    data = response.json()
    assert response.status_code == 200
    assert data["_id"] == usuario_criado["id"]
    assert data["email"] == usuario_criado["email"]
    assert data["nome"] == usuario_criado["nome"]

def test_buscar_usuario_por_id_inexistente_retorna_400(base_url):
    response = buscar_usuario(base_url,"id_invalido_que_nao_existe_xyz")
    assert response.status_code == 400

def test_atualizar_usuario_existente_retorna_200(base_url,usuario_criado):
    payload_atualizado = {
        "nome": "Nome Atualizado pelo QA",
        "email": gerar_email_unico(),
        "password": "novasenha456",
        "administrador": "false"
    }
    response = atualizar_usuario(base_url,usuario_criado["id"],payload_atualizado)
    assert response.status_code == 200
    assert response.json()["message"] == "Registro alterado com sucesso"

def test_atualizar_usuario_com_id_inexistente_cria_novo(base_url):
    payload = gerar_usuario()
    response = atualizar_usuario(base_url,"id_que_nao_existe_abc123",payload)
    data = response.json()
    assert response.status_code == 201
    assert "_id" in data
    excluir_usuario(base_url,data["_id"])
    
def test_excluir_usuario_existente_retorna_200(base_url, usuario_criado):
    response = excluir_usuario(base_url,usuario_criado["id"])
    assert response.status_code == 200
    assert response.json()["message"] == "Registro excluído com sucesso"

def test_excluir_usuario_id_inexistente_retorna_200_sem_registro(base_url):
    response = excluir_usuario(base_url,"id_que_nao_existe_para_delete")

    assert response.status_code == 200
    assert ("Nenhum registro excluído"in response.json()["message"])