import requests

def listar_usuarios(base_url):
    return requests.get(f"{base_url}/usuarios")

def criar_usuario(base_url, payload):
    return requests.post(
        f"{base_url}/usuarios",
        json=payload
    )

def buscar_usuario(base_url, user_id):
    return requests.get(
        f"{base_url}/usuarios/{user_id}"
    )

def atualizar_usuario(base_url, user_id, payload):
    return requests.put(
        f"{base_url}/usuarios/{user_id}",
        json=payload
    )

def excluir_usuario(base_url, user_id):
    return requests.delete(
        f"{base_url}/usuarios/{user_id}"
    )