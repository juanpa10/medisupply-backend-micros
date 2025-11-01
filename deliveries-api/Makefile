.PHONY: run test cov
run:
	FLASK_ENV=development python -m app.app
test:
	pytest -q --maxfail=1
cov:
	pytest -q --maxfail=1 --cov=app --cov-report=term-missing
