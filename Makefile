.PHONY: help up tools down logs ps bootstrap reset lint test

help: ## List available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start required platform services
	@docker compose up -d --wait --wait-timeout 600

tools: ## Start optional Kafka UI
	@docker compose --profile tools up -d --wait --wait-timeout 600

down: ## Stop services without deleting data
	@docker compose --profile tools down

logs: ## Follow service logs
	@docker compose --profile tools logs -f --tail=100

ps: ## Show service state
	@docker compose --profile tools ps

bootstrap: ## Create Kafka topics, MinIO buckets and check PostGIS
	@sh scripts/run-bootstrap.sh

reset: ## Remove containers and data volumes after confirmation
	@printf "This deletes all local project data. Type 'reset' to continue: "; read -r answer; test "$$answer" = "reset" || { echo "Cancelled."; exit 1; }; docker compose --profile tools down -v

lint: ## Run configured style checks
	@echo "Lint will be configured in a later phase."

test: ## Run automated tests
	@echo "Automated tests will be added in a later phase."
