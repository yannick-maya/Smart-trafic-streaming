# Dictionnaire de données

Les identifiants et noms de colonnes sont en anglais pour rester stables dans le code. Les CSV sont encodés en UTF-8, séparés par des virgules, avec une ligne d'en-tête.

## Référentiels

### `troncons.csv`

| Colonne | Type / unité | Description |
|---|---|---|
| `troncon_id` | texte | Clé stable `osm-way-<id>`; clé référencée par les capteurs. |
| `osm_way_ids` | texte | Identifiant OSM source; plusieurs IDs pourront être séparés par `;`. |
| `axis_name` | texte | `name`, puis `ref`, puis libellé OSM explicite si absent. |
| `highway_class` | enum | `trunk`, `primary`, `secondary` ou `tertiary`. |
| `lanes` | entier ou vide | Première valeur numérique du tag `lanes`. |
| `length_m` | décimal, mètres | Longueur de la polyligne calculée par somme de distances haversine. |
| `speed_limit_kmh` | décimal, km/h | Tag `maxspeed` converti si disponible; sinon valeur de démonstration par classe. |
| `free_flow_speed_kmh` | décimal, km/h | Estimation égale à 90 % de `speed_limit_kmh`, plafonnée à 80 km/h. |
| `geometry_wkt` | WKT `LINESTRING`, EPSG:4326 | Géométrie OSM; ordre des coordonnées WKT longitude puis latitude. |
| `data_origin` | `real` | Géométrie et attributs issus d'OpenStreetMap; vitesses limites manquantes sont des estimations et sont documentées. |

### `capteurs.csv`

| Colonne | Type / unité | Description |
|---|---|---|
| `capteur_id` | texte | Identifiant reproductible dérivé du way OSM et de la position. |
| `troncon_id` | texte, FK | Tronçon OSM auquel le capteur fictif est rattaché. |
| `sensor_type` | enum | `flow_speed`; mesure de démonstration débit/vitesse. |
| `latitude`, `longitude` | décimal, degrés | Positions interpolées à un tiers et deux tiers de la polyligne. |
| `data_origin` | `simulated` | Le capteur et ses mesures sont fictifs. |

### `zones.csv`

| Colonne | Type / unité | Description |
|---|---|---|
| `zone_id` | texte | Clé stable : `centre-ville`, `port`, `aeroport`, `marche`, `aflao`, `peripherie`. |
| `zone_name`, `zone_type` | texte | Libellé et catégorie analytique. |
| `latitude`, `longitude` | décimal, degrés | Centre OSM si trouvé, sinon centre conventionnel décrit dans `data-sources.md`. |
| `footprint_wkt` | WKT `POLYGON`, EPSG:4326 | Carré analytique centré sur le point de référence. |
| `footprint_method` | texte | `analytical_buffer_720m`; empreinte de démonstration, non administrative. |
| `data_origin` | `real` ou `simulated` | `real` si le centre vient d'un objet OSM; `simulated` pour les centres conventionnels. |
| `source_osm_id` | texte | `type/id` OSM, ou `documented-footprint` si le centre est conventionnel. |

## Messages Kafka

Chaque contrat est un JSON Schema Draft 2020-12 autonome dans `simulator/schemas/`. Les dates de messages sont des horodatages ISO 8601 UTC; les champs `data_origin` séparent les données observées des scénarios simulés.

| Topic | Grain | Champs métier |
|---|---|---|
| `traffic.sensor.flow` | capteur × fenêtre de 5 min | `vehicle_count_5min` (véhicules), `two_wheeler_share` (ratio 0–1). Origine `simulated`. |
| `traffic.sensor.speed` | capteur × fenêtre de 5 min | `average_speed_kmh` (km/h), `occupancy_rate` (ratio 0–1), `service_level` (A–F). Origine `simulated`. |
| `traffic.weather` | lieu × heure de valeur météo | température (°C), humidité (%), précipitations (mm), vent (km/h), visibilité (m, optionnelle). Origine `real`, sauf scénario `--force-rain` explicitement `simulated`; Forecast et réanalyse ne sont pas des mesures de station à Lomé. |
| `traffic.events` | événement simulé | type, début/fin UTC, tronçons affectés, sévérité de 1 à 5. Origine `simulated`. |
| `traffic.dlq` | message rejeté | topic source, code/raison, payload brut textuel, provenance propagée du message source. |

Tous les contrats détaillent champs requis, types, unités, énumérations, contraintes et exemples directement dans le schéma JSON.
