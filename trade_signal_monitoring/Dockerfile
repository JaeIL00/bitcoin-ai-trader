FROM python:3.12.7-slim

# 필요한 패키지 설치 (curl)
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry config virtualenvs.create false

WORKDIR /app/

COPY ./pyproject.toml ./README.md ./poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./app /app

CMD ["python3", "main.py"]