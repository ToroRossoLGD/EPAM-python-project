FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install fastapi uvicorn sqlalchemy asyncpg alembic passlib[argon2] python-jose[cryptography] pydantic-settings python-multipart boto3 pytest httpx pytest-asyncio aiosqlite ruff

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]