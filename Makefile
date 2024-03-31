include .env

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down

migrate-init:
	alembic revision --autogenerate -m "init db"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade base

truncate: migrate-down migrate-up

run-bot:
	python -m bot

tests:
	pytest tests/
.PHONY: tests

pgtests:
	docker run --name postgres --rm -d \
		-p ${TEST_PG_PORT}:${TEST_PG_PORT} \
		-e POSTGRES_USER=${TEST_PG_USER} \
		-e POSTGRES_PASSWORD=${TEST_PG_PASS} \
		-e POSTGRES_DB=${TEST_PG_DB} postgres:15 -p ${TEST_PG_PORT}

stop-pgtests:
	docker stop postgres

run-tests: pgtests tests stop-pgtests