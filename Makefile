# -----------------------------------------------------------------------------
# wallstrank-py — developer Makefile
# -----------------------------------------------------------------------------
# Uses uv (https://docs.astral.sh/uv/) for environment + dependency management,
# ruff for lint/format, ty for type checking, and pytest for tests.
# -----------------------------------------------------------------------------

# Use bash and fail fast.
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

UV ?= uv
PYTHON_DIRS := src tests

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

.PHONY: install
install: ## Install runtime + dev dependencies into .venv
	$(UV) sync --all-groups

.PHONY: lock
lock: ## Refresh uv.lock without installing
	$(UV) lock

.PHONY: upgrade
upgrade: ## Upgrade all locked dependencies
	$(UV) lock --upgrade
	$(UV) sync --all-groups

# -----------------------------------------------------------------------------
# Quality
# -----------------------------------------------------------------------------

.PHONY: format
format: ## Format code with ruff
	$(UV) run ruff format $(PYTHON_DIRS)
	$(UV) run ruff check --fix --select I $(PYTHON_DIRS)

.PHONY: format-check
format-check: ## Verify formatting without modifying files
	$(UV) run ruff format --check $(PYTHON_DIRS)

.PHONY: lint
lint: ## Run ruff lint checks
	$(UV) run ruff check $(PYTHON_DIRS)

.PHONY: lint-fix
lint-fix: ## Run ruff and apply safe autofixes
	$(UV) run ruff check --fix $(PYTHON_DIRS)

.PHONY: typecheck
typecheck: ## Run ty type checker
	$(UV) run ty check

.PHONY: test
test: ## Run the test suite
	$(UV) run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	$(UV) run pytest --cov=wallstrank --cov-report=term-missing --cov-report=xml

.PHONY: check
check: format-check lint typecheck test ## Run all CI checks locally

# -----------------------------------------------------------------------------
# Build & release
# -----------------------------------------------------------------------------

.PHONY: clean
clean: ## Remove build artifacts and caches
	rm -rf dist build *.egg-info
	rm -rf .pytest_cache .ruff_cache .ty_cache .mypy_cache htmlcov coverage.xml
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

.PHONY: build
build: clean ## Build sdist and wheel into dist/
	$(UV) build

.PHONY: publish-test
publish-test: build ## Upload to TestPyPI (requires UV_PUBLISH_TOKEN or trusted publishing)
	$(UV) publish --publish-url https://test.pypi.org/legacy/ dist/*

.PHONY: publish
publish: build ## Upload to PyPI (requires UV_PUBLISH_TOKEN or trusted publishing)
	$(UV) publish dist/*

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
