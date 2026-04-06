FROM python:3.11-slim
WORKDIR /app
COPY ml-pipeline/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ml-pipeline .
CMD ["python", "-m", "src.retrain.schedule", "--config", "config/train_config.yaml"]
