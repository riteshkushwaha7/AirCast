.PHONY: dev down backend frontend mobile seed health test-backend test-pipeline

dev:
	docker compose up --build

down:
	docker compose down

backend:
	cd backend/api && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend/web && npm run dev

mobile:
	cd frontend/mobile && npm run start

seed:
	python scripts/seed_demo_data.py

health:
	python scripts/check_system_health.py

test-backend:
	pytest backend/api/tests -q

test-pipeline:
	pytest ml-pipeline/tests -q
