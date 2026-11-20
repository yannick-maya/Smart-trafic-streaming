# Lome Smart Traffic

Plateforme locale de surveillance du trafic routier de LomÃƒÂ©, construite autour d'un pipeline de donnÃƒÂ©es en streaming.

> **Provenance des donnÃƒÂ©es :** le rÃƒÂ©seau routier OpenStreetMap et la mÃƒÂ©tÃƒÂ©o Open-Meteo sont rÃƒÂ©els. Les mesures de trafic et les ÃƒÂ©vÃƒÂ©nements sont simulÃƒÂ©s ; aucune donnÃƒÂ©e publique de capteurs de trafic pour LomÃƒÂ© n'est revendiquÃƒÂ©e.

## Architecture cible

```mermaid
flowchart LR
    OSM[OpenStreetMap\nrÃƒÂ©seau rÃƒÂ©el] --> REF[RÃƒÂ©fÃƒÂ©rentiels locaux]
    METEO[Open-Meteo\nmÃƒÂ©tÃƒÂ©o rÃƒÂ©elle] --> K[Kafka KRaft]
    SIM[Simulateur Python\ntrafic simulÃƒÂ©] --> K
    K --> N[Apache NiFi\nvalidation et routage]
    N -->|brut| S3[MinIO\ndata lake]
    N -->|nettoyÃƒÂ©| PG[PostgreSQL + PostGIS\ndata warehouse]
    N -->|rejets| DLQ[Quarantaine / DLQ]
    PG --> G[Grafana\ndashboards et alertes]
```

## Avancement

- [x] Phase 0 Ã¢â‚¬â€ initialisation et conventions
- [ ] Phase 1 Ã¢â‚¬â€ infrastructure Docker Compose
- [ ] Phase 2 Ã¢â‚¬â€ rÃƒÂ©fÃƒÂ©rentiels OSM et contrats de donnÃƒÂ©es
- [ ] Phase 3 Ã¢â‚¬â€ simulateur
- [ ] Phase 4 Ã¢â‚¬â€ ingestion NiFi et data lake
- [ ] Phase 5 Ã¢â‚¬â€ entrepÃƒÂ´t PostGIS
- [ ] Phase 6 Ã¢â‚¬â€ transformation et chargement
- [ ] Phase 7 Ã¢â‚¬â€ qualitÃƒÂ© et observabilitÃƒÂ©
- [ ] Phase 8 Ã¢â‚¬â€ alertes
- [ ] Phase 9 Ã¢â‚¬â€ dashboards Grafana
- [ ] Phase 10 Ã¢â‚¬â€ tests, CI et durcissement
- [ ] Phase 11 Ã¢â‚¬â€ documentation portfolio
- [ ] Phase 12 Ã¢â‚¬â€ release

## PrÃƒÂ©requis et dÃƒÂ©marrage

La cible est une exÃƒÂ©cution 100 % locale via Docker Compose. Installer Docker Desktop avec Compose v2, Git et Make (ou GNU Make sous Windows via WSL). Ãƒâ‚¬ partir de la phase infrastructure :

```sh
cp .env.example .env
make up
```

Les services, ports et ÃƒÂ©tapes de bootstrap seront prÃƒÂ©cisÃƒÂ©s dans les phases suivantes. La phase 0 ne dÃƒÂ©marre encore aucun service.

## DonnÃƒÂ©es et licences

Les donnÃƒÂ©es OpenStreetMap sont soumises ÃƒÂ  l'ODbL et doivent ÃƒÂªtre attribuÃƒÂ©es : Ã‚Â« Ã‚Â© OpenStreetMap contributors (ODbL) Ã‚Â». Open-Meteo est la source prÃƒÂ©vue pour la mÃƒÂ©tÃƒÂ©o ; les conditions d'utilisation et limites de requÃƒÂªtes seront documentÃƒÂ©es avant intÃƒÂ©gration. Les ÃƒÂ©vÃƒÂ©nements et mesures de trafic synthÃƒÂ©tiques seront toujours marquÃƒÂ©s `data_origin=simulated`.

## Structure

Les rÃƒÂ©pertoires `simulator/`, `nifi/`, `sql/`, `grafana/`, `scripts/`, `tests/`, `data/` et `docs/` accueillent les composants prÃƒÂ©vus. Les rÃƒÂ©pertoires encore vides sont conservÃƒÂ©s par `.gitkeep` jusqu'ÃƒÂ  leur premiÃƒÂ¨re implÃƒÂ©mentation.

## Conventions

- Documentation en franÃƒÂ§ais ; code, identifiants et commits en anglais.
- Commits selon Conventional Commits.
- Aucun secret, volume Docker ou donnÃƒÂ©e gÃƒÂ©nÃƒÂ©rÃƒÂ©e ne doit ÃƒÂªtre versionnÃƒÂ©.
- Une phase est livrÃƒÂ©e et taguÃƒÂ©e avant de commencer la suivante.
# Infrastructure locale

Les services Compose utilisent des tags d'images exacts consignÃƒÂ©s dans `.env.example`. Copier ce fichier en `.env` avant de dÃƒÂ©marrer. Les identifiants fournis sont rÃƒÂ©servÃƒÂ©s au dÃƒÂ©veloppement local.

```sh
cp .env.example .env
make up
make bootstrap
```

`make up` dÃƒÂ©marre la pile et les outils optionnels (Kafka UI). `make bootstrap` crÃƒÂ©e les topics Kafka, les buckets MinIO et vÃƒÂ©rifie PostGIS. Les scripts de bootstrap peuvent ÃƒÂªtre rejouÃƒÂ©s. Les donnÃƒÂ©es sont conservÃƒÂ©es dans des volumes Docker nommÃƒÂ©s. `make reset` les supprime aprÃƒÂ¨s confirmation.

| Service | URL locale | Identifiants |
|---|---|---|
| NiFi | https://localhost:8443/nifi | valeurs `NIFI_USERNAME` / `NIFI_PASSWORD` de `.env` |
| MinIO API | http://localhost:9000 | valeurs `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` de `.env` |
| MinIO Console | http://localhost:9001 | mÃƒÂªmes identifiants MinIO |
| Grafana | http://localhost:3000 | valeurs `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` de `.env` |
| Kafka UI | http://localhost:8080 | sans authentification, lancer avec `make tools` |
| Kafka | localhost:9092 | accÃƒÂ¨s local de dÃƒÂ©veloppement |
| PostgreSQL | localhost:5432 | valeurs `POSTGRES_USER` / `POSTGRES_PASSWORD` de `.env` |

Compose rÃƒÂ©serve environ 5,4 Gio de limites mÃƒÂ©moire pour les services, laissant une marge pour Docker et le systÃƒÂ¨me sur une machine de 8 Go. NiFi est le plus gourmand. Si la mÃƒÂ©moire disponible est infÃƒÂ©rieure, les interfaces optionnelles peuvent ÃƒÂªtre dÃƒÂ©sactivÃƒÂ©es avec `docker compose up -d kafka nifi minio postgres grafana`; MinIO bootstrap reste accessible via son service de profil.

Le broker Kafka est un nÃ…â€œud combinÃƒÂ© broker/contrÃƒÂ´leur en KRaft. Cette configuration convient au dÃƒÂ©veloppement local, pas ÃƒÂ  une installation haute disponibilitÃƒÂ©.
