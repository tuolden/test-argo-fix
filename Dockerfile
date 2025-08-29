# syntax=docker/dockerfile:1.7
ARG PY_VERSION=3.11
ARG BASE=python:${PY_VERSION}-bookworm

FROM ${BASE} AS builder
WORKDIR /app

# Avoid interactive prompts in APT
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for building (Debian-friendly; no caching of /var/lib/apt)
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (copy minimal context needed for editable install)
COPY pyproject.toml README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install --no-warn-script-location --no-cache-dir -e .

# Copy application code
COPY . .

# ===== Runtime Stage =====
FROM python:${PY_VERSION}-slim-bookworm AS runtime
WORKDIR /app

# Avoid interactive prompts in APT
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies (Debian-friendly; no caching of /var/lib/apt)
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tini \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 10001 appuser && useradd -r -u 10000 -g appuser appuser

# Copy Python packages and app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
    CMD curl -f http://127.0.0.1:8080/health || exit 1

# Use tini for signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
# Use a package-agnostic runner to avoid template placeholders
CMD ["python", "-m", "app_runner"]

# OCI labels
ARG VERSION=dev
ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="test_argo_fix" \
      org.opencontainers.image.description="Test project for Argo fix" \
      org.opencontainers.image.url="https://github.com/tuolden/test_argo_fix" \
      org.opencontainers.image.source="https://github.com/tuolden/test_argo_fix" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}"
