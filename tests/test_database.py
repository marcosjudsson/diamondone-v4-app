# tests/test_database.py
import pytest
from src.database import get_db_engine
from sqlalchemy.engine import Engine

def test_get_db_engine_and_connection():
    """
    Testa se a função get_db_engine retorna uma instância de Engine do SQLAlchemy
    e se uma conexão real com o banco de dados pode ser estabelecida.
    """
    try:
        engine = get_db_engine()
        # Verifica se o objeto retornado é uma instância da Engine do SQLAlchemy
        assert isinstance(engine, Engine), "A função não retornou um objeto Engine do SQLAlchemy."
        
        # Tenta estabelecer uma conexão para validar a URL, credenciais e configurações (como o keepalive)
        with engine.connect() as connection:
            assert not connection.closed, "A conexão foi estabelecida mas está fechada."
            
    except Exception as e:
        pytest.fail(f"A criação do engine ou a conexão com o banco de dados falhou: {e}")