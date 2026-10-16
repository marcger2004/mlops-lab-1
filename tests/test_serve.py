from io import BytesIO
import asyncio
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from src.food11 import serve


def test_predict_preprocesses_grayscale_and_maps_class(monkeypatch):
    class Model:
        def predict(self, batch):
            assert batch.shape == (1, 3, 224, 224)
            assert batch.dtype == np.float32
            logits = np.zeros((1, 11), dtype=np.float32)
            logits[0, 6] = 1000  # Stable softmax must not overflow.
            return logits

    monkeypatch.setattr(serve.app.state, "model", Model(), raising=False)
    stream = BytesIO()
    Image.new("L", (128, 128), 128).save(stream, format="PNG")
    stream.seek(0)
    result = serve.predict(UploadFile(filename="sample.png", file=stream))
    assert result == {"category": "Noodles/Pasta", "confidence": 1.0}
    assert stream.closed


def test_predict_rejects_invalid_image():
    with pytest.raises(HTTPException) as error:
        serve.predict(UploadFile(filename="bad.jpg", file=BytesIO(b"invalid")))
    assert error.value.status_code == 400


def test_startup_resolves_champion_once_and_loads_that_version(monkeypatch):
    calls = []
    model = object()

    class Client:
        def get_model_version_by_alias(self, name, alias):
            assert (name, alias) == ("food11", "champion")
            calls.append("resolve")
            return SimpleNamespace(version="2")

    def load(uri):
        calls.append(uri)
        return model

    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    monkeypatch.setattr(serve.mlflow, "set_tracking_uri", lambda uri: calls.append(uri))
    monkeypatch.setattr(serve.mlflow, "MlflowClient", Client)
    monkeypatch.setattr(serve.mlflow.pyfunc, "load_model", load)
    app = SimpleNamespace(state=SimpleNamespace())

    async def start():
        async with serve.lifespan(app):
            assert app.state.model is model

    asyncio.run(start())
    assert calls == ["http://mlflow:5000", "resolve", "models:/food11/2"]
