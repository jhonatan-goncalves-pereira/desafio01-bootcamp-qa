import requests

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