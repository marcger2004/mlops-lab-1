FROM python:3.14-slim

RUN pip install --no-cache-dir mlflow==3.16.0
RUN mkdir -p /mlflow-data
EXPOSE 5000
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "sqlite:////mlflow-data/mlflow.db", "--serve-artifacts", "--default-artifact-root", "mlflow-artifacts:/", "--artifacts-destination", "/mlflow-data/artifacts", "--allowed-hosts", "mlflow:5000,localhost:*,127.0.0.1:*"]
