# Microservice Makefile
LOGIN_APP = login_service.login:app
PID_FILE = .uvicorn.pid

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

run:
	python -m uvicorn login_service.login:app --host localhost --port 8001 --reload

start:
	nohup python -m uvicorn $(LOGIN_APP) --host 0.0.0.0 --port 8001 --reload \
	> .uvicorn.out 2>&1 & echo $$! > $(PID_FILE)
	@echo "Login service started (PID=$$(cat $(PID_FILE))) on http://localhost:8001"

stop:
	@if [ -f $(PID_FILE) ]; then \
	kill $$(cat $(PID_FILE)) && rm -f $(PID_FILE) && echo "Service stopped."; \
	else \
	echo "No PID file found. Did you use 'make start-[service]'?"; \
	fi

test:
	python -m pytest -q