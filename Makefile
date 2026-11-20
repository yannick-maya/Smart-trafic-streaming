.PHONY: help up down logs lint test

help: ## Afficher les commandes disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

up: ## Démarrer la plateforme (à partir de la phase 1)
	@docker compose up -d

down: ## Arrêter la plateforme
	@docker compose down

logs: ## Suivre les journaux des services
	@docker compose logs -f --tail=100

lint: ## Vérifications de style (à compléter)
	@echo "Lint sera configuré dans une phase ultérieure."

test: ## Tests automatisés (à compléter)
	@echo "Les tests seront ajoutés dans les phases ultérieures."
