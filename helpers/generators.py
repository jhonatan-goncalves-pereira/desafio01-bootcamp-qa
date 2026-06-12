import uuid


def gerar_email_unico():
    return f"qa_{uuid.uuid4().hex[:10]}@serverest.dev"


def gerar_usuario():
    return {
        "nome": "Usuário QA Automatizando",
        "email": gerar_email_unico(),
        "password": "teste@123",
        "administrador": "true"
    }
    
def gerar_produto():
    return {
        "nome": f"Produto QA {uuid.uuid4().hex[:8]}",
        "preco": 100,
        "descricao": "Produto criado via automação",
        "quantidade": 50
    }
