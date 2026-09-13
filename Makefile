.PHONY: install migrate seed backend frontend test test-e2e reset dev

install:
	pip install -r src/backend/requirements.txt
	cd src/frontend && npm install

migrate:
	cd src/backend && alembic upgrade head

seed:
	python src/data/generate_dataset.py
	python src/scripts/seed_demo.py

reset:
	python src/scripts/reset_demo.py

backend:
	cd src/backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd src/frontend && npm run dev

dev:
	@echo "Starting THREATMESH..."
	@echo "Run 'make backend' in terminal 1 and 'make frontend' in terminal 2."

test:
	pytest src/backend/tests -v

test-e2e:
	pytest src/backend/tests/test_demo_validation.py -v
