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
