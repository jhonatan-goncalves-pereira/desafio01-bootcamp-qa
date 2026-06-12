# 🚀 ServeRest API Test Automation

Projeto de automação de testes de API desenvolvido com Python, Pytest e Requests para validação dos principais fluxos da API ServeRest.

> Desafio desenvolvido durante o Bootcamp QA da Compass UOL (AI/R Fellowship).

---

## 🎯 Objetivo

Garantir a qualidade dos principais endpoints da API através de testes automatizados cobrindo:

- Fluxos positivos (Happy Path)
- Validações de regras de negócio
- Cenários negativos
- Isolamento dos testes
- Reutilização de código através de fixtures e helpers

---

## 🌐 API Utilizada

### ServeRest

API pública para estudos e automação de testes.

https://compassuol.serverest.dev/


---

## 🛠️ Stack Utilizada

- Python 3.10+
- Pytest
- Requests
- UUID
- Pytest Fixtures
- Pytest Configuration

---

## 📂 Arquitetura do Projeto

```text
desafio01-botcampqa-air/
│
├── helpers/
│   ├── carrinho_helper.py
│   ├── generators.py
│   ├── login_helper.py
│   ├── produtos_helper.py
│   └── usuarios_helper.py
│
├── tests/
│   ├── test_carrinho.py
│   ├── test_login.py
│   ├── test_produtos.py
│   └── test_usuarios.py
│
├── .gitignore
├── conftest.py
├── pytest.ini
├── README.md
└── requirements.txt


```

---

## 🧠 Arquitetura Adotada

O projeto segue uma abordagem baseada em:

### Helpers

Centralizam todas as chamadas HTTP para a API.

Exemplo:

```python
criar_usuario()
buscar_usuario()
atualizar_usuario()
excluir_usuario()
```

Benefícios:

- Evita duplicação de código
- Facilita manutenção
- Melhora legibilidade dos testes

---

### Generators

Responsáveis pela geração de dados dinâmicos para execução dos testes.

Exemplo:

```python
gerar_usuario()
gerar_produto()
gerar_email_unico()
```

Benefícios:

- Evita conflitos de dados
- Permite múltiplas execuções consecutivas
- Mantém os testes independentes

---

### Fixtures

Implementadas através do `conftest.py`.

Principais fixtures:

| Fixture | Responsabilidade |
|----------|------------------|
| base_url | URL base da API |
| usuario_payload | Payload dinâmico |
| usuario_criado | Cria usuário para os testes |
| token_admin | Realiza login e gera token |
| produto_criado | Cria produto para testes |

---

## ⚙️ Instalação

Clone o projeto:

```bash
git clone https://github.com/jhonatan-goncalves-pereira/desafio01-bootcamp-qa
```

Entre na pasta:

```bash
cd desafio01-bootcamp-qa
```

Crie ambiente virtual:

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux/Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Executando os Testes

Executar toda a suíte:

```bash
pytest
```

Modo detalhado:

```bash
pytest -v
```

Executar apenas usuários:

```bash
pytest tests/test_usuarios.py -v
```

Executar apenas login:

```bash
pytest tests/test_login.py -v
```

Executar apenas produtos:

```bash
pytest tests/test_produtos.py -v
```

Executar apenas carrinho:

```bash
pytest tests/test_carrinho.py -v
```

Executar um cenário específico:

```bash
pytest tests/test_login.py::test_login_com_sucesso -v
```

---

# 📊 Cobertura Atual

## 👤 Usuários

### Endpoint

```http
/api/usuarios
```

### Cenários Cobertos

✅ Listar usuários

✅ Validar campo quantidade

✅ Cadastrar usuário válido

✅ Impedir email duplicado

✅ Cadastro sem nome

✅ Cadastro sem email

✅ Cadastro sem senha

✅ Buscar usuário por ID válido

✅ Buscar usuário inexistente

✅ Atualizar usuário existente

✅ Atualizar usuário inexistente

✅ Excluir usuário existente

✅ Excluir usuário inexistente

---

## 🔐 Login

### Endpoint

```http
/api/login
```

### Cenários Cobertos

✅ Login com sucesso

---

## 📦 Produtos

### Endpoint

```http
/api/produtos
```

### Cenários Cobertos

✅ Buscar produto criado

---

## 🛒 Carrinhos

### Endpoint

```http
/api/carrinhos
```

### Cenários Cobertos

✅ Criar carrinho

✅ Buscar carrinho por ID

✅ Buscar carrinho inexistente

✅ Não permitir dois carrinhos para o mesmo usuário

✅ Produto inexistente

✅ Cancelar compra

✅ Concluir compra

---

# 📈 Estatísticas da Suíte

| Módulo | Quantidade |
|---------|------------|
| Usuários | 13 |
| Login | 1 |
| Produtos | 1 |
| Carrinho | 7 |
| **Total** | **22 testes automatizados** |

---

# 🔍 Boas Práticas Aplicadas

✅ Fixtures reutilizáveis

✅ Geração dinâmica de dados

✅ Separação de responsabilidades

✅ Helpers para centralização das chamadas HTTP

✅ Testes independentes

✅ Teardown automático

✅ Estrutura escalável

✅ Código reutilizável

✅ Padrão AAA (Arrange, Act, Assert)

---

# 🚀 Próximas Implementações

### Login

- [ ] Login com senha inválida
- [ ] Login sem email
- [ ] Login sem senha

### Produtos

- [ ] Criar produto
- [ ] Atualizar produto
- [ ] Excluir produto
- [ ] Produto duplicado
- [ ] Produto sem token

### Carrinho

- [ ] Carrinho sem token
- [ ] Quantidade inválida
- [ ] Estoque insuficiente

### Qualidade

- [ ] Relatório HTML
- [ ] Integração contínua (GitHub Actions)
- [ ] Execução automática em Pull Requests

---
