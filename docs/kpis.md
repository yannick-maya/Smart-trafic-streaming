# Définitions des indicateurs

Les fenêtres de trafic sont des intervalles UTC semi-ouverts de cinq minutes, `[t, t+5 min)`. Une agrégation par tronçon rassemble les capteurs actifs rattachés à ce tronçon. Une fenêtre sans mesure est `NULL`/absente, jamais zéro par défaut. La météo est jointe à l'heure la plus proche et reste identifiée par `data_origin`.

| Indicateur | Formule | Unité / fenêtre | Limites |
|---|---|---|---|
| Débit | `Σ vehicle_count_5min` des capteurs valides du tronçon | véhicules / 5 min | Les capteurs sont fictifs; les doublons d'événement doivent être éliminés avant somme. |
| Vitesse moyenne | `Σ(vitesse_i × débit_i) / Σ(débit_i)`; si somme débit = 0, moyenne arithmétique des vitesses présentes | km/h / 5 min | Pondération par véhicules; exclure les valeurs hors plage avant calcul. |
| Taux d'occupation | `Σ occupancy_rate_i / nombre de capteurs présents` | ratio 0–1 / 5 min; afficher en % si besoin | Moyenne simple par capteur; ne pas interpréter comme densité absolue. |
| Ratio vitesse libre | `r = clamp(vitesse_moyenne / free_flow_speed_kmh, 0, 1)` | ratio / 5 min | `free_flow_speed_kmh` est une estimation de phase 2, pas une vitesse mesurée. |
| Indice de congestion | `1 - r` | ratio 0–1 / 5 min | 0 signifie fluide selon la référence estimée; 1 signifie vitesse nulle. |
| Part des deux-roues | `Σ véhicule_deux_roues / Σ véhicules`; pour un seul capteur, `two_wheeler_share` | ratio 0–1 / 5 min | Définie à `NULL` si aucun véhicule. |
| Niveau de service | Appliquer les seuils configurables à `r`: A si `r > 0,85`; B si `0,67 < r ≤ 0,85`; C si `0,50 < r ≤ 0,67`; D si `0,40 < r ≤ 0,50`; E si `0,30 < r ≤ 0,40`; F si `r ≤ 0,30` | Lettre A–F / 5 min | Les seuils sont des règles de démonstration calibrables, non une norme locale validée. |
| Temps de parcours d'un axe | `Σ (length_m / 1000 / vitesse_moyenne_tronçon_kmh) × 60` | minutes / dernière fenêtre 5 min | Somme des tronçons ordonnés de l'axe; si une vitesse est nulle ou manquante, le résultat est indisponible. |
| Effet associé à la pluie | Différence des vitesses moyennes entre fenêtres `precipitation_mm > 0` et `= 0`, par classe de route et période | km/h; fenêtres comparables | Association descriptive seulement; jour, heure, événements et simulation peuvent confondre l'effet. |

Les fenêtres sont calculées après validation et déduplication par `event_id`. Un même `troncon_id` est la clé Kafka afin de préserver l'ordre par tronçon.
