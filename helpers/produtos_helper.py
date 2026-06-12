import requests
def criar_produto(base_url, token, payload):
    headers = {
        "Authorization": token
    }
    return requests.post(
        f"{base_url}/produtos",
        json=payload,
        headers=headers
    )

def buscar_produto(base_url, produto_id):
    return requests.get(
        f"{base_url}/produtos/{produto_id}"
    )


def excluir_produto(base_url, token, produto_id):
    headers = {
        "Authorization": token
    }
    return requests.delete(
        f"{base_url}/produtos/{produto_id}",
        headers=headers
    )