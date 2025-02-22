# Worker-FeedParser

This repository contains a Python script for parsing RSS feeds. The script runs in a continuous loop, fetching the latest feed updates.

## Features

- Continuously parses RSS feed entries in a loop and posts the extracted data to the API server.
- Easily customizable for different RSS feeds via a configuration file (`source.yaml`).

## Installation

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```

## Environment Variables

```
LNQ_API_URL = os.getenv("LNQ_API_URL", "127.0.0.1")
LNQ_API_PORT = os.getenv("LNQ_API_PORT", "8000")
```