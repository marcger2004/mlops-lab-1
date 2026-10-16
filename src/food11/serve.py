"""Serve the registered Food-11 champion with the training transforms."""
import os
import logging
from contextlib import asynccontextmanager

import mlflow
import mlflow.pyfunc
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision.models import ResNet18_Weights

from .data import FOOD11_CLASSES


@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    # Resolve once so the logged version is exactly the one loaded, even if
    # someone moves champion while the model is being downloaded.
    version = mlflow.MlflowClient().get_model_version_by_alias("food11", "champion")
    app.state.model = mlflow.pyfunc.load_model(f"models:/food11/{version.version}")
    logging.getLogger("uvicorn.error").info("Loaded food11 champion version %s", version.version)
    yield


app = FastAPI(title="Food-11 API", lifespan=lifespan)
transform = ResNet18_Weights.DEFAULT.transforms()
# ImageFolder sorts the top-level directory names used during training.
CLASSES = sorted(FOOD11_CLASSES, key=lambda name: name.split("/")[0])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(file: UploadFile = File(...)):
    try:
        with Image.open(file.file) as image:
            batch = transform(image.convert("RGB")).unsqueeze(0).numpy()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise HTTPException(status_code=400, detail="Upload a valid image.") from exc
    finally:
        file.file.close()
    logits = np.asarray(app.state.model.predict(batch), dtype=np.float32)
    if logits.shape != (1, len(CLASSES)) or not np.isfinite(logits).all():
        raise RuntimeError("Expected eleven finite class logits from the model")
    scores = np.exp(logits[0] - logits[0].max())
    scores /= scores.sum()
    index = int(scores.argmax())
    return {"category": CLASSES[index], "confidence": float(scores[index])}
