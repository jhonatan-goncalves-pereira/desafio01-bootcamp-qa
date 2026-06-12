# serverest-api-tests

Automated API tests for ServeRest using Python and Pytest — AI/R Fellowship Week 3

## Stack

- Python 3.8+
- [Pytest](https://pytest.org)
- [Requests](https://requests.readthedocs.io)
- API: [ServeRest](https://compassuol.serverest.dev)



## Pré-requisitos

- Python 3.8 ou superior
- pip

## Instalação

```bash
git clone https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa
cd desafio01-bootcamp-qa

python -m venv venv
source venv/bin/activate  
venv\Scripts\activate     

pip install -r requirements.txt
```

## Como rodar os testes

```bash
pytest

pytest -v

pytest tests/test_usuarios.py::test_listar_usuarios_retorna_status_200

pytest --html=report.html --self-contained-html
```

