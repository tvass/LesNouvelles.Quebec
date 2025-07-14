#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/prompt.py
Description: PromptClient class for interacting with the Prompt Item API.
"""

import requests
import os
from config import *
import numpy as np
import re


class PromptClient:

    def __init__(
        self,
        uuid=None,
        text=None,
        text_improved=None,
        key=None,
        tags=None,
        created_at=None,
        lastused_at=None,
        embedding=None,
        feed=None,
        settings=None,
        ner_count=None,
        enable=None,
    ):
        self.uuid = uuid
        self.text = text
        self.text_improved = text_improved
        self.key = key
        self.tags = tags or []
        self.created_at = created_at
        self.lastused_at = lastused_at
        self.embedding = embedding or []
        self.feed = feed or []
        self.settings = settings or []
        self.ner_count = ner_count or 0
        self.enable = enable or True

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
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/prompt/{self.uuid}/{self.key}"
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
            print(data)
        else:
            print(f"Failed to get Prompt: {response.text}")

    def to_dict(self):
        """Convert the Prompt to a dictionary format for API calls."""
        return {
            "uuid": self.uuid,
            "text": self.text,
            "text_improved": self.text_improved,
            "key": self.key,
            "tags": self.tags,
            "created_at": self.created_at,
            "lastused_at": self.lastused_at,
            "embedding": self.embedding,
            "feed": self.feed,
            "settings": self.settings,
            "ner_count": self.ner_count,
            "enable": self.enable
        }

    def from_dict(self, data):
        """Populate the Prompt object from a dictionary (e.g., API response)."""
        self.uuid = data.get("uuid")
        self.text = data.get("text")
        self.text_improved = data.get("text_improved")
        self.key = data.get("key")
        self.tags = data.get("tags", [])
        self.created_at = data.get("created_at")
        self.lastused_at = data.get("lastused_at")
        self.embedding = data.get("embedding", [])
        self.feed = data.get("feed", [])
        self.settings = data.get("settings", [])
        self.ner_count = data.get("ner_count", 0)
        self.enable = data.get("enable", True)

    def __str__(self):
        """Convert the Prompt to a string representation, replacing punctuation and special characters with spaces."""
        sanitized_text = re.sub(r"[^A-Za-z0-9À-ÿ\s]", " ", self.text)
        return sanitized_text


    def search(self):
        """Search for Articles using the embedding. Return > 1.5"""
        if not self.embedding:
            raise ValueError("Embedding is required to search for articles that matche me.")
        api_url = f"{LNQ_API_URL}:{LNQ_API_PORT}/search/{self.uuid}"
        response = requests.get(api_url)
        if response.status_code == 200:
            self.feed = response.json()
            print("Items retrieved successfully to build feed.")
        else:
            print(f"Failed to get Items to build feed: {response.text}")
