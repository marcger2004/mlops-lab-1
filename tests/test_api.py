import numpy as np
from fastapi.testclient import TestClient

from food11 import serve


class FakeModel:
    def predict(self, batch):
        assert batch.shape == (1, 3, 224, 224)
        return np.log([[0.90] + [0.01] * 10])


def test_health_and_missing_model(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        assert client.get("/health").status_code == 200
        with open("tests/fixtures/bread.jpg", "rb") as image:
            assert client.post("/predict", files={"file": image}).status_code == 503


def test_predict_returns_valid_json(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        monkeypatch.setattr(serve, "model", FakeModel())
        with open("tests/fixtures/bread.jpg", "rb") as image:
            response = client.post("/predict", files={"file": ("bread.jpg", image, "image/jpeg")})
    assert response.status_code == 200
    assert response.json()["category"] == "Bread"
    assert abs(response.json()["confidence"] - 0.9) < 1e-6
