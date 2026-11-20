# ADR 0001 — Architecture générale

- Statut : accepté
- Date : 2026-11-20

## Contexte

Le projet doit démontrer une chaîne de traitement de données de trafic reproductible, entièrement locale, du transport d'événements à l'analyse et à la visualisation. Le lake brut et l'entrepôt analytique répondent à des besoins distincts : conserver les messages reçus pour audit/rejeu, puis fournir des données structurées et efficaces pour les requêtes métier.

## Décision

La cible retient Kafka en mode KRaft pour les flux, NiFi pour l'ingestion et le routage, MinIO pour le stockage objet brut compatible S3, PostgreSQL avec PostGIS pour l'entrepôt et les géométries, et Grafana pour les tableaux de bord et alertes. L'ensemble est exécuté localement avec Docker Compose.

## Conséquences

Cette architecture rend visibles les responsabilités et permet le rejeu depuis les données brutes. Elle a un coût en mémoire et en exploitation ; Compose devra proposer des limites et profils adaptés à une machine modeste. Les versions d'images seront vérifiées et épinglées dans la phase infrastructure.
