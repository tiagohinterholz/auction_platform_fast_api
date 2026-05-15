import pytest


@pytest.fixture
def register_payload():
    return {
        "name": "João da Silva",
        "email": "joao@example.com",
        "cpf": "12345678901",
        "password": "Pass@123",
    }


@pytest.fixture
def login_payload():
    return {
        "email": "joao@example.com",
        "password": "Pass@123",
    }


@pytest.fixture
def update_user_payload():
    return {
        "name": "João Atualizado",
        "email": "joao.atualizado@example.com",
    }
