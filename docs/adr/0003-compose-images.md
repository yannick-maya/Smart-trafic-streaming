# ADR 0003 — Images Docker et profils Compose

- Statut : accepté avec réserve
- Date : 2026-11-20

## Contexte

La phase infrastructure doit être reproductible sur une machine locale d'environ 8 Go de mémoire. Les images doivent être épinglées et les outils auxiliaires désactivables.

## Décision

Kafka utilise l'image officielle Apache en mode KRaft combiné mono-nœud, adapté à une démonstration locale seulement. Les versions retenues sont Kafka 4.4.0, NiFi 2.7.2, PostGIS/PostgreSQL 17-3.7, Grafana 12.4.15 et Kafbat UI 1.5.0. L'UI Kafka reste dans le profil Compose `tools`. Les limites mémoire Compose laissent environ 5,4 Gio pour les conteneurs configurés, hors marge du moteur Docker et du système hôte.

L'image publique MinIO en amont est archivée et n'est plus publiée au registre d'origine. Pour conserver une image récupérable, la pile utilise le tag versionné `dappros/minio:RELEASE.2025-09-07T16-13-09Z`, annoncé comme copie byte-identique de la dernière image communautaire. Le client `mc` est versionné séparément. Les utilisateurs peuvent remplacer `MINIO_IMAGE` par un registre de confiance qu'ils contrôlent.

## Conséquences

Les tags exacts rendent les mises à jour explicites, mais ne garantissent pas à eux seuls l'immuabilité cryptographique. Un seul broker KRaft et un seul nœud de chaque service n'apportent aucune haute disponibilité. Le miroir MinIO est un risque de chaîne d'approvisionnement ; l'ADR devra être révisé si une image communautaire maintenue ou un autre magasin objet compatible est retenu. Le profil `tools` apporte Kafka UI et le client MinIO de bootstrap à la demande.
