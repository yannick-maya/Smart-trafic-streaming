# PROMPT CODEX â€” LomÃ© Smart Traffic (plateforme de streaming data engineering)

> **Mode d'emploi**
> 1. CrÃ©e un dÃ©pÃ´t Git vide (GitHub), clone-le en local et ouvre-le dans Codex.
> 2. Colle **tout le contenu ci-dessous** (de Â« RÃ”LE Â» jusqu'Ã  la fin) dans Codex. Tu peux aussi le sauvegarder sous `AGENTS.md` Ã  la racine du dÃ©pÃ´t pour que Codex le relise Ã  chaque session.
> 3. Codex exÃ©cute **une seule phase Ã  la fois**, pousse sur Git, te fait un rapport, puis attend ton Â« GO phase N Â».
> 4. Si tu veux qu'il enchaÃ®ne sans s'arrÃªter, supprime la rÃ¨gle R9 (arrÃªt aprÃ¨s chaque phase).
5. Version 2 : approche hybride (rÃ©seau OSM et mÃ©tÃ©o Open-Meteo rÃ©els, trafic simulÃ©).

---

## RÃ”LE

Tu es un **Senior Data Engineer / Streaming Architect** (10 ans d'expÃ©rience) qui travaille avec rigueur d'ingÃ©nieur : code propre, reproductible, testÃ©, documentÃ©, versionnÃ©. Tu travailles sur mon dÃ©pÃ´t Git local comme sur un projet professionnel destinÃ© Ã  mon portfolio.

## CONTEXTE DU PROJET

**Nom du projet :** `lome-smart-traffic`
**Objectif :** concevoir et implÃ©menter une plateforme **streaming (micro-batch rapprochÃ©)** de surveillance du trafic routier de **LomÃ© (Togo)**, de bout en bout : donnÃ©es hybrides (rÃ©seau routier et mÃ©tÃ©o **rÃ©els**, trafic **simulÃ©**) â†’ bus de messages â†’ ingestion/routage â†’ **data lake** (brut) â†’ **data warehouse** (modÃ¨le en Ã©toile) â†’ **dashboard analytique temps rÃ©el** (carte de congestion, KPIs, alertes).

**Nature du projet :** projet personnel de portfolio (pas d'Ã©valuation acadÃ©mique). La prioritÃ© est la **qualitÃ© d'ingÃ©nierie**, la **reproductibilitÃ©** (`make up` suffit Ã  tout lancer) et la **valeur de dÃ©monstration** (dashboard visuel, documentation claire).

**Utilisateurs mÃ©tier fictifs :** centre de supervision du trafic, opÃ©rateur de voirie, citoyens.
**DÃ©cisions facilitÃ©es :** dÃ©clenchement d'alertes de congestion, information des usagers, aide Ã  la rÃ©gulation.

## STACK IMPOSÃ‰E (100 % local, Docker Compose)

| Couche | Outil |
|---|---|
| DonnÃ©es rÃ©elles | **OpenStreetMap** (rÃ©seau routier de LomÃ©, via Overpass API ou extrait Geofabrik/HDX) ; **Open-Meteo** (mÃ©tÃ©o, API gratuite) |
| GÃ©nÃ©ration de donnÃ©es de trafic | Python 3.11+ (simulateur), producteur Kafka |
| Bus de messages | **Apache Kafka** (mode KRaft, sans ZooKeeper) |
| Ingestion / routage / transformation lÃ©gÃ¨re | **Apache NiFi** |
| Data lake (brut) | **MinIO** (compatible S3) |
| Data warehouse | **PostgreSQL + PostGIS** (schÃ©ma en Ã©toile) |
| Visualisation et alertes | **Grafana OSS** (provisioning as code) |
| QualitÃ© / tests | pytest, SQL de contrÃ´le, CI GitHub Actions |

Contraintes : tout tourne avec `docker compose`, **aucun service cloud payant**, **aucune API payante**. PrÃ©voir une machine modeste (cible : ~8 Go de RAM disponibles) : dÃ©finir des limites mÃ©moire raisonnables et des *profiles* Compose pour dÃ©sactiver les services optionnels.

**Versions :** avant de figer une image Docker ou une dÃ©pendance, vÃ©rifie la derniÃ¨re version stable compatible, **Ã©pingle des versions exactes** (jamais `latest`) et note le choix dans `docs/adr/`.

## DONNÃ‰ES : PRINCIPES (approche hybride rÃ©el + simulÃ©)

| DonnÃ©e | Statut | Source |
|---|---|---|
| RÃ©seau routier, gÃ©omÃ©tries, axes, points d'intÃ©rÃªt (port, aÃ©roport, marchÃ©, frontiÃ¨re) | **RÃ©el** | OpenStreetMap, licence ODbL |
| MÃ©tÃ©o (pluie, tempÃ©rature, humiditÃ©, vent, visibilitÃ© si disponible) | **RÃ©el** | Open-Meteo : donnÃ©es courantes en mode *live*, archive historique en mode *replay* |
| Trafic (flux, vitesses, occupation des capteurs) | **SimulÃ©** | Simulateur calibrÃ© sur le rÃ©seau rÃ©el |
| Ã‰vÃ©nements (accidents, travaux, marchÃ©, cortÃ¨ges) | **SimulÃ©** | Simulateur |

**HonnÃªtetÃ© des donnÃ©es (non nÃ©gociable)**
- Il n'existe pas de donnÃ©es publiques de capteurs de trafic pour LomÃ© : le trafic et les capteurs sont **fictifs**. Ne jamais les prÃ©senter comme des mesures rÃ©elles.
- Chaque message et chaque table doivent porter une colonne/champ d'origine `data_origin` (`real` ou `simulated`) afin que le lignage soit lisible jusqu'au dashboard.
- Le README et `docs/data-sources.md` indiquent clairement : sources, licences, dates d'extraction, limites. Attribution obligatoire : Â« Â© OpenStreetMap contributors (ODbL) Â». VÃ©rifie les conditions d'utilisation d'Open-Meteo (usage non commercial, limites de requÃªtes) et cite-les.

**RÃ©seau routier (OSM)**
- Ã‰cris `scripts/fetch_osm.py` : extraction du rÃ©seau de LomÃ© (emprise gÃ©ographique documentÃ©e, routes `highway` principales : trunk, primary, secondary, tertiary ; filtrage par nom d'axe) via Overpass API, avec `User-Agent` explicite, retries avec backoff, et respect des limites.
- **Commite un instantanÃ© rÃ©duit** (quelques Mo maximum) dans `data/reference/osm/` avec sa date d'extraction, pour qu'un clone du dÃ©pÃ´t n'ait pas besoin d'Internet pour la partie OSM. Si l'Overpass API est inaccessible, utilise un extrait Geofabrik/HDX et documente-le.
- Axes Ã  retrouver dans OSM (noms indicatifs, Ã  vÃ©rifier dans les donnÃ©es) : Boulevard du 13 Janvier, Boulevard du Mono, Boulevard Circulaire, Boulevard EyadÃ©ma, Route d'AnÃ©ho (RN2), accÃ¨s au Port autonome, accÃ¨s Ã  l'aÃ©roport, abords du Grand MarchÃ©, accÃ¨s Ã  la frontiÃ¨re d'Aflao.
- Cible : **15 Ã  25 tronÃ§ons** dÃ©rivÃ©s d'OSM et **30 Ã  60 capteurs fictifs** positionnÃ©s sur ces tronÃ§ons.

**MÃ©tÃ©o (Open-Meteo)**
- CoordonnÃ©es du centre de LomÃ© (â‰ˆ 6,13Â° N ; 1,22Â° E, Ã  vÃ©rifier et documenter).
- Mode *live* : donnÃ©es courantes/horaires. Mode *replay* : archive historique d'une pÃ©riode passÃ©e, pour rejouer une journÃ©e rÃ©elle de mÃ©tÃ©o en accÃ©lÃ©rÃ©. Consulte la documentation officielle avant d'implÃ©menter (endpoints, paramÃ¨tres, unitÃ©s).
- **Aucun test et aucune CI ne doivent appeler d'API externe** : utiliser des *fixtures* JSON commitÃ©es (petites) pour les tests.
- Si l'API est indisponible, le pipeline le signale (log + alerte) ; il ne bascule **jamais silencieusement** sur de la mÃ©tÃ©o synthÃ©tique.

**RÃ©alisme du trafic simulÃ©**
- Pointes du matin (â‰ˆ 7h-9h) et du soir (â‰ˆ 17h-19h30), forte part de **zÃ©midjans** (motos-taxis), effet de la **pluie** (baisse de vitesse, hausse de la congestion), **Ã©vÃ©nements** (accidents, travaux, marchÃ©, cortÃ¨ges), variations jour ouvrÃ© / week-end.
- Le simulateur module les vitesses selon la mÃ©tÃ©o **rÃ©elle** quand elle est disponible. Pour la dÃ©monstration, un scÃ©nario `--force-rain` injecte de la pluie synthÃ©tique, **clairement marquÃ©e** `data_origin=simulated`.

---

## RÃˆGLES GLOBALES (Ã  respecter Ã  chaque phase)

**R1 â€” Une phase Ã  la fois.** Ne commence jamais la phase suivante avant que les critÃ¨res d'acceptation de la phase en cours soient vÃ©rifiÃ©s et le push confirmÃ©.

**R2 â€” Git : commit propre + PUSH aprÃ¨s CHAQUE phase.**
- Branche de travail : `main` (projet personnel). Si aucun `origin` n'est configurÃ©, demande-moi l'URL **une seule fois**, puis configure-le.
- Commits **atomiques** en **Conventional Commits**, en anglais : `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `ci:`, `refactor:`. Exemple : `feat(simulator): add rain impact on speed profiles`.
- Ã€ la fin de **chaque phase**, exÃ©cute dans cet ordre :
  1. `git status` (rien d'inattendu, aucun secret, aucun gros fichier)
  2. `git add` ciblÃ© puis `git commit` (plusieurs commits logiques si nÃ©cessaire)
  3. `git push origin main`
  4. `git tag -a phase-NN -m "Phase NN: <titre>"` puis `git push origin --tags`
  5. VÃ©rifie le push : `git log --oneline -5` et `git status` (la branche doit Ãªtre Ã  jour avec `origin/main`).
- **Interdits :** `git push --force`, rÃ©Ã©criture de l'historique publiÃ©, commit de secrets, de volumes Docker, de donnÃ©es lourdes ou de fichiers gÃ©nÃ©rÃ©s.

**R3 â€” ReproductibilitÃ©.** Un tiers doit pouvoir cloner le dÃ©pÃ´t, copier `.env.example` en `.env`, lancer `make up` et obtenir la plateforme fonctionnelle. Aucun pas manuel non documentÃ©.

**R4 â€” SÃ©curitÃ©.** Aucun mot de passe ni clÃ© dans le dÃ©pÃ´t. Utilise `.env` (ignorÃ© par Git) et `.env.example` (valeurs factices). `.gitignore` complet dÃ¨s la phase 0.

**R5 â€” QualitÃ© de code.** Python typÃ©, formatÃ© et lintÃ© (`ruff`, `black` ou Ã©quivalent), docstrings utiles, logs structurÃ©s (JSON), gestion explicite des erreurs. SQL lisible, idempotent, versionnÃ© en migrations numÃ©rotÃ©es.

**R6 â€” Idempotence et robustesse.** Tout traitement doit pouvoir Ãªtre rejouÃ© sans doublons (clÃ©s naturelles, `INSERT ... ON CONFLICT`, dÃ©duplication). GÃ©rer donnÃ©es tardives, doublons, valeurs aberrantes et capteurs muets.

**R7 â€” HonnÃªtetÃ©.** Si tu ne peux pas vÃ©rifier quelque chose (version, comportement d'un outil, absence d'accÃ¨s rÃ©seau), dis-le explicitement. N'invente ni rÃ©sultats de tests ni sorties de commandes : **exÃ©cute rÃ©ellement** les vÃ©rifications et colle la sortie utile.

**R8 â€” Rapport de fin de phase (format obligatoire).**
1. **RÃ©sumÃ©** de ce qui a Ã©tÃ© fait (5-10 lignes)
2. **Fichiers crÃ©Ã©s/modifiÃ©s** (liste courte)
3. **VÃ©rifications exÃ©cutÃ©es** (commandes + rÃ©sultats rÃ©els)
4. **CritÃ¨res d'acceptation** : liste cochÃ©e âœ…/âŒ
5. **Push Git** : hash du dernier commit, tag crÃ©Ã©, confirmation que `origin/main` est Ã  jour
6. **Points ouverts / dÃ©cisions Ã  valider** (max 3)

**R9 â€” ArrÃªt aprÃ¨s chaque phase.** AprÃ¨s le rapport, **arrÃªte-toi** et attends mon message Â« GO phase N Â». Ne pose pas de questions en cours de phase sauf blocage rÃ©el ; en cas d'ambiguÃ¯tÃ© mineure, choisis l'option la plus raisonnable et documente-la dans `docs/adr/`.

**R10 â€” Documentation continue.** Chaque dÃ©cision d'architecture notable fait l'objet d'un ADR court dans `docs/adr/` (contexte, dÃ©cision, consÃ©quences). La documentation est rÃ©digÃ©e en **franÃ§ais** ; le code, les identifiants, les noms de tables et les messages de commit en **anglais**.

---

## ARCHITECTURE CIBLE

```
OpenStreetMap (rÃ©seau, rÃ©fÃ©rentiels)     Open-Meteo (mÃ©tÃ©o rÃ©elle)
        â”‚ (instantanÃ© commitÃ©)                     â”‚ NiFi InvokeHTTP
        â–¼                                          â–¼
Simulateur Python (capteurs flux/vitesse, Ã©vÃ©nements)   â”€â”€â–º  topic traffic.weather
        â”‚  JSON, topics Kafka
        â–¼
   Apache Kafka (KRaft)
        â”‚
        â–¼
   Apache NiFi â”€â”€ validation / enrichissement / routage
     â”œâ”€â”€ invalides â”€â”€â–º topic DLQ + MinIO  (bucket traffic-quarantine)
     â”œâ”€â”€ brut â”€â”€â”€â”€â”€â”€â”€â–º MinIO               (bucket traffic-raw, partitionnÃ© date/heure)
     â””â”€â”€ nettoyÃ© â”€â”€â”€â”€â–º PostgreSQL + PostGIS (staging â†’ schÃ©ma en Ã©toile)
                                â”‚
                                â–¼
                  Vues KPIs + rÃ¨gles d'alerte
                                â”‚
                                â–¼
                 Grafana (carte de congestion, KPIs, alertes)
```

**Topics Kafka :** `traffic.sensor.flow`, `traffic.sensor.speed`, `traffic.weather`, `traffic.events`, `traffic.dlq`. ClÃ© de message = `troncon_id` (ordre garanti par tronÃ§on). DÃ©finir partitions et rÃ©tention de faÃ§on justifiÃ©e.

**Structure du dÃ©pÃ´t attendue :**

```
lome-smart-traffic/
â”œâ”€â”€ README.md
â”œâ”€â”€ AGENTS.md                # (optionnel) ce prompt
â”œâ”€â”€ Makefile
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ .env.example
â”œâ”€â”€ .gitignore
â”œâ”€â”€ .github/workflows/ci.yml
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ architecture.md      # schÃ©ma Mermaid + explications
â”‚   â”œâ”€â”€ data-dictionary.md
â”‚   â”œâ”€â”€ data-sources.md      # sources, licences, attributions
â”‚   â”œâ”€â”€ kpis.md
â”‚   â”œâ”€â”€ runbook.md
â”‚   â”œâ”€â”€ lineage.md
â”‚   â””â”€â”€ adr/
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ reference/           # troncons.csv, capteurs.csv, zones.csv (dÃ©rivÃ©s d'OSM)
â”‚   â”œâ”€â”€ osm/                 # instantanÃ© OSM commitÃ© (ODbL)
â”‚   â””â”€â”€ fixtures/            # petits JSON pour les tests (mÃ©tÃ©o)
â”œâ”€â”€ simulator/               # code Python + tests
â”œâ”€â”€ nifi/                    # flows exportÃ©s (JSON), scripts d'import, drivers
â”œâ”€â”€ sql/
â”‚   â”œâ”€â”€ migrations/          # 001_*.sql, 002_*.sql ...
â”‚   â”œâ”€â”€ views/
â”‚   â””â”€â”€ checks/              # contrÃ´les qualitÃ©
â”œâ”€â”€ grafana/
â”‚   â”œâ”€â”€ provisioning/        # datasources, dashboards, alerting
â”‚   â””â”€â”€ dashboards/          # JSON versionnÃ©s
â”œâ”€â”€ scripts/                 # bootstrap MinIO, Kafka topics, NiFi, smoke test
â””â”€â”€ tests/                   # tests d'intÃ©gration / e2e
```

---

# PHASES

## PHASE 0 â€” Initialisation du dÃ©pÃ´t et conventions
**Tag :** `phase-00`

**TÃ¢ches**
- Initialiser la structure du dÃ©pÃ´t (voir ci-dessus), `.gitignore` (Python, Docker, `.env`, volumes, donnÃ©es gÃ©nÃ©rÃ©es, IDE), `.editorconfig`, licence MIT.
- `README.md` initial : pitch du projet, avertissement sur l'origine des donnÃ©es (rÃ©seau et mÃ©tÃ©o rÃ©els, trafic simulÃ©), schÃ©ma d'architecture (Mermaid), prÃ©requis, statut d'avancement par phase.
- `Makefile` avec cibles de base : `help`, `up`, `down`, `logs`, `lint`, `test` (vides ou minimales Ã  ce stade).
- Configurer `origin` si nÃ©cessaire, premier push de `main`.
- CrÃ©er `docs/adr/0001-architecture-overview.md` (pourquoi Kafka + NiFi + MinIO + PostGIS + Grafana, et la distinction lake / warehouse) et `docs/adr/0002-hybrid-data-strategy.md` (rÃ©el vs simulÃ©, raisons, limites).

**CritÃ¨res d'acceptation**
- DÃ©pÃ´t clonÃ© propre, structure en place, `make help` fonctionne.
- Premier push effectuÃ©, tag `phase-00` visible sur le distant.

## PHASE 1 â€” Infrastructure Docker Compose
**Tag :** `phase-01`

**TÃ¢ches**
- Ã‰crire `docker-compose.yml` avec : Kafka (KRaft), Kafka UI (profil optionnel), NiFi, MinIO, PostgreSQL+PostGIS, Grafana. RÃ©seau dÃ©diÃ©, volumes nommÃ©s, **healthchecks** pour chaque service, `depends_on` avec conditions de santÃ©, limites mÃ©moire raisonnables.
- `.env.example` complet (ports, identifiants factices, noms de buckets, paramÃ¨tres Kafka).
- Scripts d'amorÃ§age idempotents dans `scripts/` : crÃ©ation des topics Kafka, des buckets MinIO (`traffic-raw`, `traffic-quarantine`), vÃ©rification de PostGIS.
- Cibles Makefile : `up`, `down`, `ps`, `bootstrap`, `reset` (avec confirmation).
- Documenter les URLs/ports locaux (NiFi, MinIO console, Grafana, Kafka UI) dans le README.

**CritÃ¨res d'acceptation**
- `make up && make bootstrap` dÃ©marre tous les services en Ã©tat *healthy*.
- Topics et buckets crÃ©Ã©s ; `SELECT postgis_version();` fonctionne.
- Relancer `make bootstrap` deux fois ne produit aucune erreur (idempotence).

## PHASE 2 â€” RÃ©fÃ©rentiels de LomÃ© (OSM) et contrats de donnÃ©es
**Tag :** `phase-02`

**TÃ¢ches**
- ImplÃ©menter `scripts/fetch_osm.py`, produire l'**instantanÃ© OSM** commitÃ© (voir Â« DonnÃ©es : principes Â»), puis un script de transformation qui gÃ©nÃ¨re :
  - `data/reference/troncons.csv` : `troncon_id`, `osm_way_id(s)`, nom de l'axe, type de route, nombre de voies, longueur (calculÃ©e), vitesse limite (tag OSM `maxspeed` si prÃ©sent, sinon valeur par dÃ©faut documentÃ©e par type de route), vitesse libre estimÃ©e (rÃ¨gle documentÃ©e), gÃ©omÃ©trie WKT ;
  - `data/reference/zones.csv` : zones (centre-ville, port, aÃ©roport, marchÃ©, frontiÃ¨re, pÃ©riphÃ©rie) Ã  partir de points d'intÃ©rÃªt OSM ou d'emprises documentÃ©es ;
  - `data/reference/capteurs.csv` : capteurs **fictifs** (flux/vitesse) rattachÃ©s Ã  un tronÃ§on, avec position sur la gÃ©omÃ©trie.
- Documenter prÃ©cisÃ©ment la sÃ©lection et les hypothÃ¨ses dans `docs/data-sources.md` (emprise, filtres, valeurs par dÃ©faut, date d'extraction, licence ODbL, attribution).
- DÃ©finir les **contrats de donnÃ©es** (JSON Schema) pour chaque topic dans `simulator/schemas/` : champs, types, unitÃ©s, valeurs autorisÃ©es, exemples, champ `data_origin`.
- RÃ©diger `docs/data-dictionary.md` (rÃ©fÃ©rentiels + Ã©vÃ©nements).
- RÃ©diger `docs/kpis.md` : dÃ©finition **prÃ©cise** de chaque KPI (formule, unitÃ©, fenÃªtre) :
  - dÃ©bit (vÃ©hicules / 5 min), vitesse moyenne, **taux d'occupation**, indice de congestion (`1 - vitesse/vitesse_libre`), part de deux-roues, **niveau de service Aâ†’F** (seuils sur le ratio vitesse/vitesse libre, ex. A > 0,85 ; B > 0,67 ; C > 0,50 ; D > 0,40 ; E > 0,30 ; F â‰¤ 0,30, **configurables**), temps de parcours estimÃ© par axe.

**CritÃ¨res d'acceptation**
- Le script OSM s'exÃ©cute (ou, hors ligne, la transformation fonctionne Ã  partir de l'instantanÃ© commitÃ©) et rÃ©gÃ©nÃ¨re les CSV de faÃ§on dÃ©terministe.
- CSV valides et cohÃ©rents (clÃ©s Ã©trangÃ¨res entre fichiers vÃ©rifiÃ©es par un test), gÃ©omÃ©tries valides.
- SchÃ©mas JSON valides, dictionnaire de donnÃ©es, dÃ©finitions de KPIs et `docs/data-sources.md` relus et sans ambiguÃ¯tÃ©.

## PHASE 3 â€” Simulateur de donnÃ©es temps rÃ©el
**Tag :** `phase-03`

**TÃ¢ches**
- Package Python `simulator/` : CLI (`python -m simulator --mode live|replay --speed 60 --seed 42 --duration ...`), configuration via fichier YAML/ENV, **graine alÃ©atoire reproductible**, **accÃ©lÃ©ration du temps** configurable. Mode `live` : temps rÃ©el, mÃ©tÃ©o courante. Mode `replay` : rejoue une pÃ©riode passÃ©e avec la mÃ©tÃ©o historique rÃ©elle correspondante.
- GÃ©nÃ©rateurs : flux vÃ©hicules et vitesses toutes les 5 min par capteur (avec part de zÃ©midjans), Ã©vÃ©nements (accidents, travaux, marchÃ©, cortÃ¨ge) avec dÃ©but/fin et **impact sur les tronÃ§ons voisins**. La **mÃ©tÃ©o n'est plus gÃ©nÃ©rÃ©e** par dÃ©faut : le simulateur lit la mÃ©tÃ©o rÃ©elle (topic `traffic.weather` ou cache/fixture en replay) pour moduler les vitesses ; l'option `--force-rain` produit de la pluie synthÃ©tique marquÃ©e `data_origin=simulated`.
- Profils rÃ©alistes : pointes matin/soir, creux de nuit, week-end, effet pluie, saturation progressive puis dissipation.
- **Injection contrÃ´lÃ©e d'anomalies** (paramÃ©trable) pour tester la qualitÃ© : doublons, valeurs hors plage, capteur muet, message tardif, champs manquants, JSON invalide.
- Producteur Kafka robuste (retries, `acks`, clÃ© = `troncon_id`, sÃ©rialisation JSON validÃ©e par schÃ©ma), arrÃªt propre.
- Conteneurisation du simulateur (service Compose avec profil `sim`).
- Tests `pytest` : reproductibilitÃ© par graine, conformitÃ© aux schÃ©mas, plages de valeurs, effet pluie/Ã©vÃ©nements, taux d'anomalies injectÃ©es.

**CritÃ¨res d'acceptation**
- `make sim` produit des messages visibles dans Kafka UI (flux, vitesses, Ã©vÃ©nements) ; la mÃ©tÃ©o provient de la phase 4 ou des fixtures en test.
- Tests verts, lint propre, mÃªmes donnÃ©es Ã  graine identique.

## PHASE 4 â€” Ingestion NiFi : validation, quarantaine, data lake
**Tag :** `phase-04`

**TÃ¢ches**
- Construire les flux NiFi : `ConsumeKafka` â†’ validation du schÃ©ma/contrat â†’ routage :
  - **valides** â†’ Ã©criture brute dans MinIO (`traffic-raw`), partitionnÃ©e `topic=<t>/date=YYYY-MM-DD/hour=HH/`, format JSON (ou Parquet si pertinent, avec justification en ADR) ;
  - **invalides** â†’ publication sur `traffic.dlq` **et** Ã©criture dans `traffic-quarantine` avec la raison du rejet.
- ParamÃ©trage via **Parameter Contexts** (aucune valeur en dur), contrÃ´leurs de services (Kafka, AWS/S3 pour MinIO), gestion du *back-pressure*.
- **Versionner les flows** : export JSON dans `nifi/flows/`, script `scripts/nifi_import.sh` (ou Ã©quivalent via l'API REST) pour rÃ©importer automatiquement les flows au dÃ©marrage. Documenter comment rÃ©-exporter aprÃ¨s modification.
- **Flux mÃ©tÃ©o rÃ©elle** : processeur `InvokeHTTP` planifiÃ© (frÃ©quence documentÃ©e, ex. toutes les 15 Ã  60 min) vers l'API Open-Meteo â†’ extraction/normalisation JSON (types, unitÃ©s, fuseau `Africa/Lome`) â†’ publication sur `traffic.weather` avec `data_origin=real`, puis passage par la mÃªme validation et le mÃªme stockage brut que les autres flux. Gestion des erreurs HTTP, retries, cache et respect des limites de l'API.
- **Script de backfill** `scripts/backfill_weather.py` : charge l'archive historique Open-Meteo d'une pÃ©riode donnÃ©e (pour le mode `replay`), avec cache local et sortie vers le topic ou un fichier de rejeu.
- Cible Makefile : `nifi-import`, `nifi-export`, `weather-backfill`.

**CritÃ¨res d'acceptation**
- AprÃ¨s `make up && make nifi-import && make sim`, des objets apparaissent dans `traffic-raw` avec le bon partitionnement.
- Les messages invalides injectÃ©s arrivent dans `traffic-quarantine` / `traffic.dlq` avec leur motif.
- Les flows sont versionnÃ©s et rÃ©importables sur une plateforme vierge.
- Des mesures mÃ©tÃ©o **rÃ©elles** de LomÃ© arrivent sur `traffic.weather` (`data_origin=real`) et dans `traffic-raw` ; en cas d'API indisponible, une erreur claire est journalisÃ©e (pas de bascule silencieuse).

## PHASE 5 â€” Data warehouse PostGIS (schÃ©ma en Ã©toile)
**Tag :** `phase-05`

**TÃ¢ches**
- Migrations SQL numÃ©rotÃ©es (`sql/migrations/`), exÃ©cutÃ©es automatiquement par un script idempotent (`make migrate`).
- SchÃ©mas : `staging` (donnÃ©es d'atterrissage), `dwh` (modÃ¨le analytique), `ops` (monitoring, alertes).
- **Dimensions :** `dim_troncon` (avec gÃ©omÃ©trie PostGIS, index GiST), `dim_capteur`, `dim_zone`, `dim_temps` (grain 5 min, avec jour/heure/pointe/week-end), `dim_meteo`, `dim_evenement_type`. Toutes les tables de faits et la mÃ©tÃ©o conservent la colonne `data_origin` (`real` / `simulated`).
- **Faits :** `fact_trafic_5min` (grain : tronÃ§on Ã— 5 min : dÃ©bit, vitesse moyenne, occupation, part deux-roues, niveau de service), `fact_evenement`, `fact_meteo_horaire`.
- Contraintes d'intÃ©gritÃ©, clÃ©s, index adaptÃ©s, **upserts idempotents** (`ON CONFLICT`), chargement des dimensions depuis `data/reference/`.
- Vues KPIs dans `sql/views/` (ex. `v_kpi_trafic_courant`, `v_niveau_service_par_troncon`, `v_impact_pluie`, `v_top_congestion`) alignÃ©es sur `docs/kpis.md`.
- Jeu de donnÃ©es de test SQL pour valider les vues sans dÃ©pendre du streaming.

**CritÃ¨res d'acceptation**
- `make migrate` fonctionne sur base vierge et en relance (idempotent).
- Les vues retournent des rÃ©sultats cohÃ©rents sur le jeu de test ; plans d'exÃ©cution sans scan inutile sur les requÃªtes principales (`EXPLAIN` joint au rapport).

## PHASE 6 â€” NiFi â†’ PostgreSQL : transformation, agrÃ©gation, chargement
**Tag :** `phase-06`

**TÃ¢ches**
- ComplÃ©ter les flows NiFi : lecture des messages valides, normalisation (types, fuseau horaire `Africa/Lome`, unitÃ©s), **dÃ©duplication**, jointure avec les rÃ©fÃ©rentiels, agrÃ©gation par fenÃªtre de 5 min, chargement dans `staging` puis `dwh` (`PutDatabaseRecord`, driver JDBC montÃ© proprement).
- Gestion des **donnÃ©es tardives** (stratÃ©gie documentÃ©e : fenÃªtre de tolÃ©rance, mise Ã  jour par upsert).
- Planification (scheduling) pour un rafraÃ®chissement continu Ã  frÃ©quence configurable (1 Ã  5 min).
- Test bout en bout automatisÃ© (`scripts/smoke_test.sh` ou test pytest) : lancer le simulateur sur une durÃ©e courte avec graine fixe, attendre, vÃ©rifier le nombre de lignes dans `traffic-raw` et `dwh.fact_trafic_5min`, et l'absence de doublons.

**CritÃ¨res d'acceptation**
- Les faits se remplissent en continu ; relancer le simulateur avec la mÃªme graine ne crÃ©e **aucun doublon**.
- Le smoke test passe de faÃ§on rÃ©pÃ©table.

## PHASE 7 â€” QualitÃ© des donnÃ©es et observabilitÃ© du pipeline
**Tag :** `phase-07`

**TÃ¢ches**
- ContrÃ´les qualitÃ© SQL dans `sql/checks/` (complÃ©tude, plages de valeurs, unicitÃ© des clÃ©s de fait, fraÃ®cheur, orphelins rÃ©fÃ©rentiels) exÃ©cutables via `make dq` avec code de sortie non nul en cas d'Ã©chec.
- Tables `ops` : volumes ingÃ©rÃ©s, taux de rejet par motif, latence de bout en bout (Ã©vÃ©nement â†’ entrepÃ´t), fraÃ®cheur par tronÃ§on, historique des contrÃ´les.
- DÃ©tection des **capteurs muets** (aucune mesure sur N intervalles) et des dÃ©rives de flux.
- Journaux structurÃ©s JSON cÃ´tÃ© simulateur et scripts ; documenter les points de contrÃ´le dans `docs/runbook.md`.

**CritÃ¨res d'acceptation**
- `make dq` dÃ©tecte correctement les anomalies injectÃ©es (test automatisÃ© qui injecte puis vÃ©rifie la dÃ©tection).
- Les mÃ©triques d'exploitation sont interrogeables en SQL.

## PHASE 8 â€” Alertes
**Tag :** `phase-08`

**TÃ¢ches**
- RÃ¨gles d'alerte configurables (seuils dans une table ou un fichier de config) : **congestion** (niveau de service E/F persistant sur N intervalles), **accident** (Ã©vÃ©nement + chute brutale de vitesse), **capteur muet**, **dÃ©gradation qualitÃ©** (taux de rejet).
- Table `ops.alerte` (horodatage, type, sÃ©vÃ©ritÃ©, tronÃ§on, statut, message) alimentÃ©e par des requÃªtes/vues planifiÃ©es ; anti-bruit (dÃ©duplication, rÃ©solution automatique).
- Alerting Grafana provisionnÃ© as code (rÃ¨gles + point de contact de dÃ©monstration, par exemple webhook ou e-mail local de test).

**CritÃ¨res d'acceptation**
- Un scÃ©nario simulÃ© de congestion + pluie + accident dÃ©clenche les alertes attendues, puis les rÃ©sout.
- Tests automatisÃ©s sur la logique d'alerte (cas nominaux et anti-bruit).

## PHASE 9 â€” Dashboards Grafana (as code)
**Tag :** `phase-09`

**TÃ¢ches**
- Provisioning automatique : datasource PostgreSQL, dossiers, dashboards JSON versionnÃ©s dans `grafana/dashboards/`.
- **Dashboard Â« Supervision du trafic â€” LomÃ© Â»** :
  - **carte de congestion** par tronÃ§on (panneau Geomap, couleurs selon niveau de service Aâ†’F) ;
  - KPIs en direct : vitesse moyenne rÃ©seau, dÃ©bit, taux d'occupation, nombre de tronÃ§ons en E/F (**au moins 5 KPIs**) ;
  - Ã©volution temporelle par axe, comparaison jour ouvrÃ©/week-end, **impact de la pluie** ;
  - liste des alertes actives et Ã©vÃ©nements en cours ;
  - filtres par zone/axe et pÃ©riode, rafraÃ®chissement automatique.
- **Dashboard Â« SantÃ© du pipeline Â»** : volumes, rejets, latence, fraÃ®cheur, capteurs muets.
- Afficher sur le dashboard la **provenance des donnÃ©es** (mention Â« RÃ©seau et mÃ©tÃ©o : rÃ©els Â· Trafic : simulÃ© Â», attribution OpenStreetMap) et la mÃ©tÃ©o rÃ©elle courante de LomÃ©.
- Soin du design : palette cohÃ©rente, titres clairs, unitÃ©s, seuils colorÃ©s, descriptions de panneaux.
- Captures d'Ã©cran dans `docs/img/` et courte vidÃ©o/GIF de dÃ©mo (script de capture documentÃ©).

**CritÃ¨res d'acceptation**
- Sur plateforme vierge, `make up` suffit pour retrouver les dashboards prÃªts, alimentÃ©s dÃ¨s que le simulateur tourne.
- La carte se met Ã  jour en continu et reflÃ¨te un scÃ©nario de pointe + pluie.

## PHASE 10 â€” Tests, CI et durcissement
**Tag :** `phase-10`

**TÃ¢ches**
- Workflow GitHub Actions : lint (ruff/black), tests unitaires (`pytest`), validation `docker compose config`, lint SQL (ex. `sqlfluff`), exÃ©cution du smoke test si les ressources de l'exÃ©cuteur le permettent (sinon version allÃ©gÃ©e documentÃ©e).
- Pre-commit hooks (formatage, dÃ©tection de secrets).
- Revue de sÃ©curitÃ© de base : pas de secrets, images Ã©pinglÃ©es, ports exposÃ©s minimaux, utilisateurs non-root quand possible.
- Cible `make test` unifiÃ©e (unitaires + intÃ©gration).

**CritÃ¨res d'acceptation**
- CI verte sur `main` ; badge de statut dans le README.
- `make lint && make test` passent en local.

## PHASE 11 â€” Documentation finale et mise en valeur portfolio
**Tag :** `phase-11`

**TÃ¢ches**
- `README.md` final : pitch, captures, architecture (Mermaid), dÃ©marrage en 5 commandes, structure du dÃ©pÃ´t, choix techniques et compromis, limites connues, pistes d'Ã©volution (ex. Flink/Spark Structured Streaming, dÃ©tection d'anomalies ML, prÃ©vision de congestion).
- `docs/architecture.md` (vue d'ensemble, flux, lake vs warehouse, justification des choix), `docs/lineage.md` (lignage des donnÃ©es de la source au dashboard), `docs/runbook.md` (dÃ©marrage, arrÃªt, incidents courants, rejeu, purge), `docs/data-dictionary.md` Ã  jour, `docs/data-sources.md` Ã  jour (sources, licences, attributions, limites).
- Script de **dÃ©monstration** (`docs/demo-script.md`) : scÃ©nario de 5 minutes (pointe du matin, pluie, accident, alertes) avec les commandes Ã  lancer.
- Section Â« DonnÃ©es : rÃ©el vs simulÃ© Â» (tableau de provenance et limites), et section Â« Ce que ce projet dÃ©montre Â» (compÃ©tences) rÃ©digÃ©e sobrement et factuellement.

**CritÃ¨res d'acceptation**
- Une personne extÃ©rieure peut lancer et comprendre le projet uniquement avec le README.
- Tous les liens et commandes de la documentation sont vÃ©rifiÃ©s.

## PHASE 12 â€” Release
**Tag :** `v1.0.0`

**TÃ¢ches**
- Passage final : `make lint test dq`, `git status` propre, nettoyage des fichiers inutiles.
- `CHANGELOG.md` et release GitHub `v1.0.0` (notes de version, captures).
- DerniÃ¨re vÃ©rification du dÃ©marrage Ã  froid sur un dÃ©pÃ´t fraÃ®chement clonÃ©.
- Push final et tag `v1.0.0`.

**CritÃ¨res d'acceptation**
- DÃ©marrage Ã  froid rÃ©ussi depuis un clone neuf, CI verte, release publiÃ©e.

---

## PREMIÃˆRE INSTRUCTION

Commence **uniquement par la PHASE 0**. Applique toutes les rÃ¨gles globales (R1 Ã  R10), termine par le **push Git** et le **rapport de fin de phase (R8)**, puis **arrÃªte-toi** et attends mon message Â« GO phase 1 Â».