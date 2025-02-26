FROM python:3.12.7-slim

# 시스템 패키지 업데이트 및 필요한 의존성 설치
RUN apt-get update && apt-get install -y \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libatspi2.0-0 \
    libasound2 \
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
RUN poetry run playwright install chromium

COPY ./app /app

# 컨테이너 실행 명령 정의
CMD ["python3", "main.py"]