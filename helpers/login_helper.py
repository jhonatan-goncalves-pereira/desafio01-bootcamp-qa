import requests

# Timeout em segundos para chamadas ao endpoint /login.
# A instância compassuol.serverest.dev trava indefinidamente para
# usuários criados dinamicamente; 10 s evita que a suite inteira trave.
LOGIN_TIMEOUT = 10


def realizar_login(base_url, email, password):
    payload = {
        "email": email,
        "password": password,
    }
    return requests.post(
        f"{base_url}/login",
        json=payload,
        timeout=LOGIN_TIMEOUT,
    )