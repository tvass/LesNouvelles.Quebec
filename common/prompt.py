#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/prompt.py
Description: PromptClient class for interacting with the Prompt Item API.
"""

import requests
import os
from config import *
import cohere as cohereV2
import numpy as np
from spacy_llm.models import cohere
from spacy_llm.util import assemble


class PromptClient:
    def __init__(
        self,
        uuid=None,
        text=None,
        key=None,
        tags=None,
        tags_embedding=None,
        created_at=None,
        lastused_at=None,
        embedding=None,
    ):
        self.uuid = uuid
        self.text = text
        self.key = key
        self.tags = tags or []
        self.tags_embedding = tags_embedding or []
        self.created_at = created_at
        self.lastused_at = lastused_at
        self.embedding = embedding or []

        if uuid:
            self.get()

    def create(self):
        """Create a new Prompt via the API (POST)."""
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/prompt"
        response = requests.post(api_url, json=self.to_dict())
        if response.status_code == 201:
            print("Prompt created successfully.")
        else:
            print(f"Failed to create Prompt: {response.text}")

    def update(self):
        """Update the existing Prompt via the API (PUT)."""
        if not self.uuid:
            raise ValueError("UUID is required to update a prompt.")
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/prompt/{self.uuid}"
        response = requests.put(api_url, json=self.to_dict())
        if response.status_code == 200:
            print("Prompt updated successfully.")
        else:
            print(f"Failed to update Prompt: {response.text}")

    def get(self):
        """Retrieve a Prompt from the API (GET)."""
        if not self.uuid:
            raise ValueError("UUID is required to get a prompt.")
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/prompt/{self.uuid}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            self.from_dict(data)
            print("Prompt retrieved successfully.")
        else:
            print(f"Failed to get Prompt: {response.text}")

    def to_dict(self):
        """Convert the Prompt to a dictionary format for API calls."""
        return {
            "uuid": self.uuid,
            "text": self.text,
            "key": self.key,
            "tags": self.tags,
            "tags_embedding": self.tags_embedding,
            "created_at": self.created_at,
            "lastused_at": self.lastused_at,
            "embedding": self.embedding,
        }

    def from_dict(self, data):
        """Populate the Prompt object from a dictionary (e.g., API response)."""
        self.uuid = data.get("uuid")
        self.text = data.get("text")
        self.key = data.get("key")
        self.tags = data.get("tags", [])
        self.tags_embedding = data.get("tags_embedding", [])
        self.created_at = data.get("created_at")
        self.lastused_at = data.get("lastused_at")
        self.embedding = data.get("embedding", [])

    def to_string(self):
        """Convert the Prompt to a string representation."""
        return str(self.text)

    def get_ner(self):
        """Get the NER for the given text using spacy-llm (configured to use Cohere API)."""
        nlp = assemble("../config/config.ner")
        text = self.to_string()
        print(f"Processing text: '{text}'")
        doc = nlp(self.text)
        ner = {
            "entities": [{"label": ent.label_, "text": ent.text} for ent in doc.ents]
        }

        self.tags = ner["entities"]

    def get_embedding(self):
        """Get the embedding for the given text using Cohere API."""
        co = cohereV2.Client(api_key=CO_API_KEY)
        emb = co.embed(
            texts=[self.to_string()],
            model="embed-multilingual-v3.0",
            input_type="search_query",
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

    def search_items(self, n=10):
        """Search for items using the embedding."""
        if not self.embedding:
            raise ValueError("Embedding is required to search for similar prompts.")
