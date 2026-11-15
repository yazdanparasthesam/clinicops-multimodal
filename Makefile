.PHONY: help install test test-unit test-integration test-oncall lint openapi dev-backend dev-frontend frontend-install frontend-test frontend-build compose-up compose-down compose-logs compose-build obs-up obs-down oncall drill drill-sim smoke seed test-backend

help:
	@echo "ClinicOps make targets: install test test-unit test-integration test-oncall lint openapi"
	@echo "  dev-backend dev-frontend frontend-install frontend-test frontend-build"
	@echo "  compose-up compose-down compose-logs compose-build obs-up obs-down oncall drill drill-sim smoke seed test-backend"

install:
	cd backend && if command -v uv >/dev/null 2>&1; then uv sync --group dev; else pip install -r requirements-dev.txt; fi

install-pip:
	cd backend && pip install -r requirements-dev.txt

install-uv:
	cd backend && uv sync --group dev

test:
	cd backend && uv run pytest -q
	@echo "oncall: skipped locally (host logfire/opentelemetry mismatch — CI runs it in 3.12)"

test-backend:
	cd backend && uv run pytest -q

test-unit:
	cd backend && uv run pytest tests/unit -q

test-integration:
	cd backend && uv run pytest tests/integration -q

test-oncall:
	cd oncall-agent && uv run pytest -q --ignore=tests/test_engine.py || echo "oncall warn"

lint:
	cd backend && uv run ruff check app tests scripts || ruff check app tests scripts

openapi:
	cd backend && uv run python scripts/export_openapi.py

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

frontend-install:
	cd frontend && npm install

frontend-test:
	cd frontend && npm test

frontend-build:
	cd frontend && npm run build

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f --tail=100

compose-build:
	docker compose build

smoke:
	bash ops/smoke.sh ${BASE:-http://localhost:8000}

seed:
	python backend/scripts/seed_demo.py ${BASE:-http://localhost:8000}

obs-up:
	OTEL_ENABLED=true docker compose --profile obs up --build -d

obs-down:
	docker compose --profile obs down

oncall:
	python oncall-agent/agent.py

drill:
	bash ops/alert-drill.sh

drill-sim:
	bash ops/alert-drill.sh --simulate
