# Simple Makefile to run local CI tasks

SHELL := /usr/bin/bash

.PHONY: help venv install fmt lint type test cov sec ci docker-build k8s-validate

VENV := .venv
ACT := . $(VENV)/bin/activate

-include .env

help:
	@echo "Targets:"
	@echo "  venv           - create virtualenv in .venv"
	@echo "  install        - install dev/test deps into .venv"
	@echo "  fmt            - run black to format"
	@echo "  lint           - run ruff checks"
	@echo "  type           - run mypy"
	@echo "  test           - run pytest"
	@echo "  cov            - run pytest with coverage report"
	@echo "  sec            - run pip-audit (dependency vulnerabilities)"
	@echo "  ci             - run lint, format check, type, tests, pip-audit"
	@echo "  docker-build   - build local dev image"
	@echo "  k8s-validate   - server-side dry-run of kustomize overlay"

venv:
	# In CI we prefer a clean venv to avoid partial/dirty states
	[ -z "$$CI" ] || rm -rf $(VENV)
	python3 -m venv $(VENV) --upgrade-deps
	$(ACT); python -m pip install --upgrade pip setuptools wheel

install: venv
	$(ACT); pip install -e '.[dev,test]'
	$(ACT); pip install pip-audit

fmt:
	$(ACT); black src/ tests/

lint:
	$(ACT); ruff check src/ tests/

type:
	$(ACT); mypy src/

test:
	$(ACT); pytest -v

cov:
	$(ACT); pytest -v --cov=src --cov-report=term-missing --cov-report=xml

sec:
	@echo "Running pip-audit (dependency vulnerability scan)"
	$(ACT); pip-audit || true

ci: lint fmt type test sec

# Docker build (Debian-friendly)
# - Forces BuildKit
# - Supports buildx with --platform
# - Allows overriding docker binary (e.g., DOCKER="sudo docker")
export DOCKER_BUILDKIT=1
DOCKER ?= docker
IMAGE ?= local/$(shell basename $$(pwd)):dev

docker-build:
	@if $(DOCKER) buildx version >/dev/null 2>&1; then \
		echo "Building linux/amd64 image with buildx"; \
		$(DOCKER) buildx build --platform=linux/amd64 --load -t $(IMAGE) . ; \
	else \
		echo "docker buildx not found; building natively (expected amd64 on server)"; \
		$(DOCKER) build -t $(IMAGE) . ; \
	fi

k8s-validate:
	kubectl apply -f k8s/base/namespace.yaml
	kubectl apply -k k8s/production --dry-run=server

