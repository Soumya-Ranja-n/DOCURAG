up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build

down:
	docker compose down

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check app tests evaluation
	cd frontend && npm run lint

ingest-demo:
	python scripts/ingest_demo.py

eval:
	cd backend && python evaluation/eval.py
