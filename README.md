# Lome Smart Traffic

Plateforme locale de surveillance du trafic routier de LomÃ©, construite autour d'un pipeline de donnÃ©es en streaming.

> **Provenance des donnÃ©es :** le rÃ©seau routier OpenStreetMap et la mÃ©tÃ©o Open-Meteo sont rÃ©els. Les mesures de trafic et les Ã©vÃ©nements sont simulÃ©s ; aucune donnÃ©e publique de capteurs de trafic pour LomÃ© n'est revendiquÃ©e.

## Architecture cible

```mermaid
flowchart LR
    OSM[OpenStreetMap\nrÃ©seau rÃ©el] --> REF[RÃ©fÃ©rentiels locaux]
    METEO[Open-Meteo\nmÃ©tÃ©o rÃ©elle] --> K[Kafka KRaft]
    SIM[Simulateur Python\ntrafic simulÃ©] --> K
    K --> N[Apache NiFi\nvalidation et routage]
    N -->|brut| S3[MinIO\ndata lake]
    N -->|nettoyÃ©| PG[PostgreSQL + PostGIS\ndata warehouse]
    N -->|rejets| DLQ[Quarantaine / DLQ]
    PG --> G[Grafana\ndashboards et alertes]
```

## Avancement

- [x] Phase 0 â€” initialisation et conventions
- [ ] Phase 1 â€” infrastructure Docker Compose
- [ ] Phase 2 â€” rÃ©fÃ©rentiels OSM et contrats de donnÃ©es
- [ ] Phase 3 â€” simulateur
- [ ] Phase 4 â€” ingestion NiFi et data lake
- [ ] Phase 5 â€” entrepÃ´t PostGIS
- [ ] Phase 6 â€” transformation et chargement
- [ ] Phase 7 â€” qualitÃ© et observabilitÃ©
- [ ] Phase 8 â€” alertes
- [ ] Phase 9 â€” dashboards Grafana
- [ ] Phase 10 â€” tests, CI et durcissement
- [ ] Phase 11 â€” documentation portfolio
- [ ] Phase 12 â€” release

## PrÃ©requis et dÃ©marrage

La cible est une exÃ©cution 100 % locale via Docker Compose. Installer Docker Desktop avec Compose v2, Git et Make (ou GNU Make sous Windows via WSL). Ã€ partir de la phase infrastructure :

```sh
cp .env.example .env
make up
```

Les services, ports et Ã©tapes de bootstrap seront prÃ©cisÃ©s dans les phases suivantes. La phase 0 ne dÃ©marre encore aucun service.

## DonnÃ©es et licences

Les donnÃ©es OpenStreetMap sont soumises Ã  l'ODbL et doivent Ãªtre attribuÃ©es : Â« Â© OpenStreetMap contributors (ODbL) Â». Open-Meteo est la source prÃ©vue pour la mÃ©tÃ©o ; les conditions d'utilisation et limites de requÃªtes seront documentÃ©es avant intÃ©gration. Les Ã©vÃ©nements et mesures de trafic synthÃ©tiques seront toujours marquÃ©s `data_origin=simulated`.

## Structure

Les rÃ©pertoires `simulator/`, `nifi/`, `sql/`, `grafana/`, `scripts/`, `tests/`, `data/` et `docs/` accueillent les composants prÃ©vus. Les rÃ©pertoires encore vides sont conservÃ©s par `.gitkeep` jusqu'Ã  leur premiÃ¨re implÃ©mentation.

## Conventions

- Documentation en franÃ§ais ; code, identifiants et commits en anglais.
- Commits selon Conventional Commits.
- Aucun secret, volume Docker ou donnÃ©e gÃ©nÃ©rÃ©e ne doit Ãªtre versionnÃ©.
- Une phase est livrÃ©e et taguÃ©e avant de commencer la suivante.
# Infrastructure locale

Les services Compose utilisent des tags d'images exacts consignÃ©s dans `.env.example`. Copier ce fichier en `.env` avant de dÃ©marrer. Les identifiants fournis sont rÃ©servÃ©s au dÃ©veloppement local.

```sh
cp .env.example .env
make up
make bootstrap
```

`make up` dÃ©marre la pile et les outils optionnels (Kafka UI). `make bootstrap` crÃ©e les topics Kafka, les buckets MinIO et vÃ©rifie PostGIS. Les scripts de bootstrap peuvent Ãªtre rejouÃ©s. Les donnÃ©es sont conservÃ©es dans des volumes Docker nommÃ©s. `make reset` les supprime aprÃ¨s confirmation.

| Service | URL locale | Identifiants |
|---|---|---|
| NiFi | https://localhost:8443/nifi | valeurs `NIFI_USERNAME` / `NIFI_PASSWORD` de `.env` |
| MinIO API | http://localhost:9000 | valeurs `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` de `.env` |
| MinIO Console | http://localhost:9001 | mÃªmes identifiants MinIO |
| Grafana | http://localhost:3000 | valeurs `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` de `.env` |
| Kafka UI | http://localhost:8080 | sans authentification, lancer avec `make tools` |
| Kafka | localhost:9092 | accÃ¨s local de dÃ©veloppement |
| PostgreSQL | localhost:5432 | valeurs `POSTGRES_USER` / `POSTGRES_PASSWORD` de `.env` |

Compose rÃ©serve environ 5,4 Gio de limites mÃ©moire pour les services, laissant une marge pour Docker et le systÃ¨me sur une machine de 8 Go. NiFi est le plus gourmand. Si la mÃ©moire disponible est infÃ©rieure, les interfaces optionnelles peuvent Ãªtre dÃ©sactivÃ©es avec `docker compose up -d kafka nifi minio postgres grafana`; MinIO bootstrap reste accessible via son service de profil.

Le broker Kafka est un nÅ“ud combinÃ© broker/contrÃ´leur en KRaft. Cette configuration convient au dÃ©veloppement local, pas Ã  une installation haute disponibilitÃ©.
