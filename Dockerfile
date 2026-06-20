FROM public.ecr.aws/lambda/python:3.12

# Lambda Web Adapter extension
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

ENV PORT=8080
ENV AWS_LWA_READINESS_CHECK_PATH=/health

WORKDIR ${LAMBDA_TASK_ROOT}

# Reproducible deps from existing lockfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-hashes -o requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Application source (includes models.yaml config)
COPY src/ ${LAMBDA_TASK_ROOT}/

ENV PYTHONPATH=${LAMBDA_TASK_ROOT}

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
