# ADR 0003 — Images Docker et profils Compose

- Statut : accepté avec réserve
- Date : 2026-11-20

## Contexte

La phase infrastructure doit fonctionner localement sur une machine d'environ 8 Go de mémoire. Les images sont épinglées et les outils auxiliaires restent optionnels.

## Décision

Kafka utilise Apache Kafka 4.4.0 en mode KRaft mono-nœud. Les versions retenues sont NiFi 2.7.2, PostGIS/PostgreSQL 17-3.7, Grafana 12.4.15 et Kafbat UI 1.5.0. L'interface Kafka est dans le profil Compose `tools`. Les limites mémoire déclarées totalisent environ 5,4 Gio, hors moteur Docker et système hôte.

L'image communautaire MinIO n'est plus publiée sur son registre d'origine. La pile utilise le tag épinglé `dappros/minio:RELEASE.2025-09-07T16-13-09Z`, annoncé comme copie byte-identique de la dernière image communautaire. Le bootstrap réutilise la commande `mc` incluse dans cette image afin d'éviter une dépendance à une seconde image dont le registre est devenu inaccessible.

NiFi ne monte pas son répertoire `conf` dans un dossier hôte vide : l'image doit conserver ses fichiers de démarrage. Ses dépôts de base de données, de flux, de contenu, de provenance et d'état sont persistés sous `.docker-data/nifi/` sur D:.

## Conséquences

Les tags explicites rendent les mises à jour visibles, mais ne garantissent pas seuls l'immuabilité cryptographique. Un broker et un nœud par service ne fournissent aucune haute disponibilité. Le miroir MinIO constitue un risque de chaîne d'approvisionnement. La pile est destinée à une démonstration locale.
