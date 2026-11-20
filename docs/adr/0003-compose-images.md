# ADR 0003 â€” Images Docker et profils Compose

- Statut : acceptÃ© avec rÃ©serve
- Date : 2026-11-20

## Contexte

La phase infrastructure doit Ãªtre reproductible sur une machine locale d'environ 8 Go de mÃ©moire. Les images doivent Ãªtre Ã©pinglÃ©es et les outils auxiliaires dÃ©sactivables.

## DÃ©cision

Kafka utilise l'image officielle Apache en mode KRaft combinÃ© mono-nÅ“ud, adaptÃ© Ã  une dÃ©monstration locale seulement. Les versions retenues sont Kafka 4.4.0, NiFi 2.7.2, PostGIS/PostgreSQL 17-3.7, Grafana 12.4.15 et Kafbat UI 1.5.0. L'UI Kafka reste dans le profil Compose `tools`. Les limites mÃ©moire Compose laissent environ 5,4 Gio pour les conteneurs configurÃ©s, hors marge du moteur Docker et du systÃ¨me hÃ´te.

L'image publique MinIO en amont est archivÃ©e et n'est plus publiÃ©e au registre d'origine. Pour conserver une image rÃ©cupÃ©rable, la pile utilise le tag versionnÃ© `dappros/minio:RELEASE.2025-09-07T16-13-09Z`, annoncÃ© comme copie byte-identique de la derniÃ¨re image communautaire. Le client `mc` est versionnÃ© sÃ©parÃ©ment. Les utilisateurs peuvent remplacer `MINIO_IMAGE` par un registre de confiance qu'ils contrÃ´lent.

## ConsÃ©quences

Les tags exacts rendent les mises Ã  jour explicites, mais ne garantissent pas Ã  eux seuls l'immuabilitÃ© cryptographique. Un seul broker KRaft et un seul nÅ“ud de chaque service n'apportent aucune haute disponibilitÃ©. Le miroir MinIO est un risque de chaÃ®ne d'approvisionnement ; l'ADR devra Ãªtre rÃ©visÃ© si une image communautaire maintenue ou un autre magasin objet compatible est retenu. Le profil `tools` apporte Kafka UI et le client MinIO de bootstrap Ã  la demande.
