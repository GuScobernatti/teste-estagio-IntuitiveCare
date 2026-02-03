import pandas as pd
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_list_operadoras():
    response = client.get("/api/operadoras")
    assert response.status_code == 200
    data = response.json()
    assert "operators" in data
    assert "total" in data
    assert data["limit"] == 10


def test_api_estatisticas():
    response = client.get("/api/estatisticas")
    assert response.status_code == 200
    data = response.json()
    assert "top_5_operadoras" in data
    assert "distribuicao_uf" in data


def test_api_operadora_nao_encontrada():
    response = client.get("/api/operadoras/00000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Operadora não encontrada"
