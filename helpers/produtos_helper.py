import requests


def listar_produtos(base_url, params=None):
    return requests.get(f"{base_url}/produtos", params=params)


def criar_produto(base_url, token, payload):
    headers = {"Authorization": token}
    return requests.post(f"{base_url}/produtos", json=payload, headers=headers)


def criar_produto_sem_token(base_url, payload):
    return requests.post(f"{base_url}/produtos", json=payload)


def buscar_produto(base_url, produto_id):
    return requests.get(f"{base_url}/produtos/{produto_id}")


def atualizar_produto(base_url, token, produto_id, payload):
    headers = {"Authorization": token}
    return requests.put(f"{base_url}/produtos/{produto_id}", json=payload, headers=headers)


def excluir_produto(base_url, token, produto_id):
    headers = {"Authorization": token}
    return requests.delete(f"{base_url}/produtos/{produto_id}", headers=headers)
