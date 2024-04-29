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

build-bot:
	docker build . -t ${BOT_IMAGE}

# решил не делать через композ на сервере для более точной настройки
init-network:
	docker network create -d bridge ${DOCKER_NETWORK}

init-redis-network:
	docker network connect --alias redis ${DOCKER_NETWORK} bot-redis

init-redis-container:
	docker run --name bot-redis -d \
		--restart always \
		redis:latest

init-pg-network:
	docker network connect --alias postgres ${DOCKER_NETWORK} bot-postgres

init-pg-container:
	docker run --name bot-postgres -d \
			--restart always \
			-p ${PG_PORT}:${PG_PORT} \
    		-e POSTGRES_USER=${PG_USER} \
    		-e POSTGRES_PASSWORD=${PG_PASS} \
    		-e POSTGRES_DB=${PG_DB} postgres:15

run-redis: init-redis-container init-redis-network

run-postgres: init-pg-container init-pg-network

run-services: run-redis run-postgres

stop-services:
	docker stop bot-postgres && docker stop bot-redis

rm-services:
	docker rm bot-postgres && docker rm bot-redis

kill-services: stop-services rm-services

run-bot:
	docker run --name bot -d \
		-p 5000:5000 --restart always \
		--env-file docker.env --network ${DOCKER_NETWORK} \
		${BOT_IMAGE} sh -c "alembic upgrade head && python -m bot"

remove-bot:
	docker stop bot && docker rm bot