#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/rss_item.py
Description: RSSItemClient class for interacting with the RSS Item API.
"""

import json
import requests
import os
from config import *
import cohere as cohereV2
import numpy as np
from spacy_llm.models import cohere
from spacy_llm.util import assemble


class RSSItemClient:

    def __init__(
        self,
        uuid=None,
        link=None,
        title=None,
        description=None,
        pubDate=None,
        source=None,
        categorie=None,
        frontpage_id=None,
        tags=None,
        tags_embedding=None,
        embedding=None,
    ):
        self.uuid = uuid
        self.link = link
        self.title = title
        self.description = description
        self.pubDate = pubDate
        self.source = source
        self.categorie = categorie
        self.frontpage_id = frontpage_id
        self.tags = tags or []
        self.tags_embedding = tags_embedding or []
        self.embedding = embedding or []

        if uuid:
            self.get()

    def create(self):
        """Create a new RSSItem via the API (POST)."""
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/rss-item"
        response = requests.post(api_url, json=self.to_dict())
        if response.status_code == 201 or response.status_code == 200:
            print(f"{response.status_code} RSS Item created successfully.")
        else:
            print(f"Failed to create RSS Item: {response.status_code} {response.text}")

    def update(self):
        """Update the existing RSSItem via the API (PUT)."""
        if not self.uuid:
            raise ValueError("UUID is required to update an RSS item.")
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/rss-item/{self.uuid}"
        response = requests.put(api_url, json=self.to_dict())
        if response.status_code == 200:
            print("RSS Item updated successfully.")
        else:
            print(f"Failed to update RSS Item: {response.status_code} {response.text}")

    def get(self):
        """Retrieve an RSSItem from the API (GET)."""
        if not self.uuid:
            raise ValueError("UUID is required to get an RSS item.")
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/rss-item/{self.uuid}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            self.from_dict(data)
            print("RSS Item retrieved successfully.")
        else:
            print(f"Failed to get RSS Item: {response.text}")

    def to_dict(self):
        """Convert the RSSItem to a dictionary format for API calls."""
        return {
            "uuid": self.uuid,
            "link": self.link,
            "title": self.title,
            "description": self.description,
            "pubDate": self.pubDate,
            "source": self.source,
            "categorie": self.categorie,
            "frontpage_id": self.frontpage_id if self.frontpage_id is not None else 0,
            "tags": self.tags,
            "tags_embedding": self.tags_embedding,
            "embedding": self.embedding,
        }

    def from_dict(self, data):
        """Populate the RSSItem object from a dictionary (e.g., API response)."""
        self.uuid = data.get("uuid")
        self.link = data.get("link")
        self.title = data.get("title")
        self.description = data.get("description")
        self.pubDate = data.get("pubDate")
        self.source = data.get("source")
        self.categorie = data.get("categorie")
        self.frontpage_id = data.get("frontpage_id", 0)
        self.tags = data.get("tags", [])
        self.tags_embedding = data.get("tags_embedding", [])
        self.embedding = data.get("embedding", [])

    def to_string(self):
        """Convert the RSSItem to a string representation."""
        return self.title + " " + self.description

    def get_ner(self):
        """Get the NER for the given text using spacy-llm (configured to use Cohere API."""
        nlp = assemble(LNQ_CONFIG_PATH + "config.ner")
        doc = nlp(self.to_string())
        ner = {
            "entities": [{"label": ent.label_, "text": ent.text} for ent in doc.ents]
        }
        self.tags = ner["entities"]

    def get_embedding(self):
        """Get the embedding for the given text using Cohere API, including metadata."""
        co = cohereV2.Client(api_key=CO_API_KEY)
        metadata = str(
            f"Source: {self.source}, Categorie: {self.categorie}, Tags: {json.dumps(self.tags)}"
        )
        emb = co.embed(
            texts=[str(self.title), str(self.description), str(metadata)],
            model="embed-multilingual-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )
        self.embedding = emb.embeddings.float[0]

    def get_tags_embedding(self):
        """Get the embedding for the tags using Cohere API."""
        if not self.tags:
            raise ValueError("Tags are required to get the tags embedding.")
        co = cohereV2.Client(api_key=CO_API_KEY)
        emb = co.embed(
            texts=[str(self.tags)],
            model="embed-multilingual-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        )
        self.tags_embedding = emb.embeddings.float[0]
