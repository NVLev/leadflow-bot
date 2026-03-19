FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml poetry.lock* ./

RUN uv pip install --system --no-cache -r pyproject.toml

COPY . .

CMD ["python", "main.py"]