# LesNouvelles.quebec
This repository contains the source code for all components of the `LesNouvelles.quebec` platform. It is designed to provide users with an improved experience for reading news articles and personalizing their feed through natural language prompts, free from the algorithms imposed by GAFAM.

## Main Features in Development
- Simple landing page offering an overview of all news from Quebec media, with direct links to the original sources.
- Allow users to easily configure a news feed using natural language prompts.
- Identify trending news.
- Provide a real-time visual indicator demonstrating a diverse range of sources.
- No registration required, as the system operates with unique URLs.


Currently, the database only retains links to articles published within the last ~48 hours, with a limit of 1000 entries. These numbers provide a good balance but can easily be adjusted. The goal is to redirect users to the original source rather than archiving any content. You can run it locally or contribute to the main site by submitting news feed configurations directly through a merge request on source.yaml.

## Architecture Overview
The architecture follows a simple micro-service design.

### Frontend (`/frontend`)

A web application that allows users to browse article links and customize prompts.
Users can also be redirected to the original articles on the source platforms.
Communicates with the API Server for all data interactions.

### FeedParser (`/worker-feedparser`)

Crawls RSS feeds continuously to extract article links and metadata.
Utilizes spaCy for Named Entity Recognition (NER) to extract key entities (locations, persons, organizations).
Sends extracted data to the API Server using HTTP POST requests.
Does not directly interact with the database, ensuring consistent data validation through the API Server.

### NER (`/worker-ner`)

This worker performs `NER` (Name Entity Recognition) extractions on users Prompts and Articles.
After processing, It updates the entity by posting to the API.
The file `app.py` utilizes `SpaCy`, while `app-using-cohere.py` uses `SpaCy-LLM` with the Cohere API.


### FeedMaker (`/worker-feedmaker`)

WIP

### API Server (`/backend`)

Powered by FastAPI.
Manages all read and write operations to the SQLite database.
Exposes endpoints for:
CRUD operations on prompts.
Retrieving article links and metadata for the frontend.
Accepting new articles from the FeedParser.
Ensures that only one process writes to the database, avoiding conflicts.

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

### Summary of the GPL v3 License:
You are free to use, modify, and distribute the code, as long as you include the same license in all copies or substantial portions of the software.
Any modifications or derived works must also be distributed under the GPL v3 license.
The software is provided "as is", without warranty of any kind.