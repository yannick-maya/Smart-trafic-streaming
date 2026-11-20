# ADR 0002 — Stratégie de données hybride

- Statut : accepté
- Date : 2026-11-20

## Contexte

Les données publiques de capteurs de trafic pour Lomé ne sont pas disponibles pour ce projet. Une démonstration utile peut combiner des référentiels géographiques et météorologiques réels avec un trafic simulé, à condition de rendre cette différence explicite partout.

## Décision

Le réseau routier proviendra d'OpenStreetMap et la météo d'Open-Meteo. Les débits, vitesses, occupations des capteurs et événements seront simulés. Chaque message et table portera `data_origin` (`real` ou `simulated`) afin de préserver la provenance.

## Conséquences

Le projet peut démontrer un pipeline sur un contexte local pertinent sans présenter des mesures fictives comme des observations. L'usage des données OSM implique l'attribution « © OpenStreetMap contributors (ODbL) ». Les conditions d'Open-Meteo, les dates d'extraction et les limites des sources seront consignées avant leur intégration.
