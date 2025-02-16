FROM python:3.12.7-slim

# 시스템 패키지 업데이트 및 필요한 의존성 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app/

# Poetry 설정: 가상환경 생성하지 않음
RUN poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/

# 의존성 설치
RUN poetry install --no-root --only main
RUN poetry run playwright install

COPY ./app /app
ENV PYTHONPATH=/app

# 컨테이너 실행 명령 정의
CMD ["python3", "main.py"]