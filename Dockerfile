# ---- builder: resolves dependencies and installs the project into a venv ----
FROM python:3.13-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

# Deps first, app code after: this layer only invalidates when
# pyproject.toml/uv.lock change, not on every source edit.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

# ---- runtime: just Python + the built venv, no uv/pip/build tools ----
FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
