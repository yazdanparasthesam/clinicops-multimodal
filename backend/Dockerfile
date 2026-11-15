FROM python:3.12-slim
WORKDIR /app
# use uv for fast installs if available, fallback to pip
COPY requirements.txt pyproject.toml* ./
RUN pip install --no-cache-dir uv && \
    if [ -f pyproject.toml ]; then uv pip install --system -r requirements.txt; else pip install --no-cache-dir -r requirements.txt; fi
COPY app ./app
COPY scripts ./scripts
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
