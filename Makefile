up:
	docker compose up --build

down:
	docker compose down -v

test-backend:
	docker run --rm -v $(PWD)/backend:/app -w /app python:3.11 bash -lc "pip install -r requirements.txt && pytest -q"

package:
	bash scripts/build_release.sh /workspace open-payments-hub.tar.gz