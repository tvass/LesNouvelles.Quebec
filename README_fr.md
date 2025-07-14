# LesNouvelles.quebec
Ce dépôt contient le code source de tous les composants de la plateforme `LesNouvelles.quebec`. Il est conçu pour offrir aux utilisateurs une expérience agréable de lecture des nouvelles et de personnalisation de leur flux grâce à des prompts en langage naturel, sans dépendre des algorithmes imposés par les GAFAM.


## Fonctionnalités principales en développement
- Une page d'accueil simple offrant un aperçu de toutes les actualités des médias québécois, avec des liens directs vers les sources originales.
- Permettre aux utilisateurs de personnaliser un flux d'actualités en langage naturel.
- Détecter les sujets chauds.
- Fournir un indicateur visuel en temps réel démontrant une diversité des sources.
- Aucune inscription requise, le système fonctionne avec des URL uniques.


Actuellement, la base de données ne conserve que les liens vers les articles publiés au cours des ~48 dernières heures, avec une limite de 1000 entrées. Ces chiffres assurent un bon équilibre mais peuvent être ajustés facilement. L'objectif est de rediriger les utilisateurs vers la source originale plutôt que d'archiver le contenu. Vous pouvez l'exécuter localement ou contribuer au site principal en soumettant directement les configurations de flux d'actualités via une merge request sur `source.yaml`.

## Vue d'ensemble de l'architecture
L'architecture suit un design simple en microservices.

### Frontend (`/frontend`)
Une application web permettant aux utilisateurs de parcourir des liens d'articles et de personnaliser les invites. Les utilisateurs peuvent également être redirigés vers les articles originaux sur les plateformes sources. Elle communique avec le serveur API pour toutes les interactions de données.

### FeedParser (`/worker-feedparser`)
Analyse les flux RSS en continu pour extraire les liens d'articles et les métadonnées. Utilise spaCy pour la reconnaissance d'entités nommées (NER) afin d'extraire des entités clés (lieux, personnes, organisations). Envoie les données extraites au serveur API via des requêtes HTTP POST. N'interagit pas directement avec la base de données, garantissant ainsi une validation cohérente des données via le serveur API.

### NER (`/worker-ner`)

Ce worker effectue des extractions `NER` (Name Entity Recognition) sur les `Prompts` et les `Articles`.
Après le traitement, le service met à jour l'entité en postant sur l'API.
Le fichier `app.py` utilise `SpaCy`, tandis que `app-using-cohere.py` utilise `SpaCy-LLM` avec l'API Cohere.

### FeedMaker (`/worker-feedmaker`)

WIP

### API Server (`/backend`)
Propulsé par FastAPI. Gère toutes les opérations de lecture et d'écriture sur la base de données SQLite.
Expose des endpoints pour :

- Les opérations CRUD sur les prompts.
- Récupérer les liens d'articles et les métadonnées pour le frontend.
- Enregistrer les nouveaux articles du FeedParser. Seul processus qui écrit dans la base de données, évitant ainsi les conflits.

## License
Ce projet est sous licence GNU General Public License v3.0 - consultez le fichier LICENSE pour plus de détails.

### Résumé de la licence GPL v3 :
Vous êtes libre d'utiliser, de modifier et de distribuer le code, tant que vous incluez la même licence dans toutes les copies ou portions substantielles du logiciel.
Toute modification ou œuvre dérivée doit également être distribuée sous la licence GPL v3.
Le logiciel est fourni "tel quel", sans garantie d'aucune sorte.