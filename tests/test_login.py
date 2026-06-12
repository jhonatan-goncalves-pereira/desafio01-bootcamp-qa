from helpers.login_helper import realizar_login


def test_login_com_sucesso(base_url, usuario_criado):

    response = realizar_login(
        base_url,
        usuario_criado["email"],
        usuario_criado["password"]
    )

    assert response.status_code == 200

    body = response.json()

    assert "authorization" in body
    assert body["message"] == "Login realizado com sucesso"