import requests


def listar_carrinhos(base_url, params=None):
    return requests.get(f"{base_url}/carrinhos", params=params)


def criar_carrinho(base_url, token, produto_id, quantidade=1):
    headers = {"Authorization": token}
    payload = {
        "produtos": [
            {
                "idProduto": produto_id,
                "quantidade": quantidade,
            }
        ]
    }
    return requests.post(f"{base_url}/carrinhos", json=payload, headers=headers)


def buscar_carrinho(base_url, carrinho_id):
    return requests.get(f"{base_url}/carrinhos/{carrinho_id}")


def cancelar_compra(base_url, token):
    headers = {"Authorization": token}
    return requests.delete(f"{base_url}/carrinhos/cancelar-compra", headers=headers)


def concluir_compra(base_url, token):
    headers = {"Authorization": token}
    return requests.delete(f"{base_url}/carrinhos/concluir-compra", headers=headers)
