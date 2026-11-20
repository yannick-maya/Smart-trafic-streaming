# ADR 0004 — Snapshot et dérivation des référentiels OSM

- Statut : accepté
- Date : 2026-11-20

## Contexte

La démonstration doit pouvoir reconstruire ses référentiels hors ligne et séparer les géométries OSM des capteurs fictifs. Une extraction Overpass récurrente ou une dépendance à l'API pendant les tests irait à l'encontre de cet objectif.

## Décision

Une extraction manuelle unique et bornée de Lomé est conservée dans `data/reference/osm/lome-roads.json`, avec sa date, sa requête, son emprise et son attribution. Le script utilise un `User-Agent`, un timeout, des retries espacés et une limite de taille; il ne lance pas de requêtes en parallèle. `build_references.py` transforme le snapshot sans réseau, choisit jusqu'à 20 voies de manière déterministe et place deux capteurs simulés par géométrie.

Les limites `maxspeed` sont lues quand elles sont interprétables; les valeurs par classe et la vitesse libre dérivée à 90 % sont des hypothèses de démonstration. Les zones sans POI OSM adapté ont des centres et emprises analytiques explicitement marqués.

## Conséquences

Un clone peut régénérer les CSV sans Internet avec `python scripts/build_references.py`. Le snapshot OSM et les référentiels dérivés doivent porter l'attribution ODbL. Les voies sélectionnées et limites cartographiques doivent être révisées si le snapshot est renouvelé; les capteurs ne sont jamais des données réelles.
