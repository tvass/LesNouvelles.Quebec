# Backend

This is the backend API server for the `LesNouvelles.quebec` platform, powered by [FastAPI](https://fastapi.tiangolo.com/).
It handles the retrieval of article links, metadata, prompts, and supplies all necessary data to the frontend web application.
This service is the only process allowed to open the database in write mode to prevent any conflicts.

## Features

- Endpoints for retrieving article links and associated metadata.
- Endpoints for CRUD operations for all objects (articles, prompts, etc.) in the database.
- Communication with the frontend app via API calls.
- Filesystem read and write operations to the SQLite database.
- Scalable architecture designed for easy future expansion.

## Requirements

- Python 3.7+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) (ASGI server)

To install the necessary dependencies:

```bash
pip install -r requirements.txt
```
