FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY services/api/pyproject.toml ./pyproject.toml
COPY services/api/app ./app
COPY services/api/tests ./tests

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .[dev]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
