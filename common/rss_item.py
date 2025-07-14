#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/rss_item.py
Description: RSSItemClient class for interacting with the RSS Item class
and Backend API.
"""

import json
import requests
import os
import re
from config import *

class RSSItemClient:

    def __init__(
        self,
        uuid=None,
        link=None,
        title=None,
        description=None,
        pubDate=None,
        ogp=None,
        image=None,
        source=None,
        categorie=None,
        frontpage_id=None,
        tags=None,
        embedding=None,
        similar=None,
        ner_count=None,
    ):
        self.uuid = uuid
        self.link = link
        self.title = title
        self.description = description
        self.pubDate = pubDate
        self.ogp = ogp or []
        self.image = image
        self.source = source
        self.categorie = categorie
        self.frontpage_id = frontpage_id
        self.tags = tags or []
        self.embedding = embedding or []
        self.similar = similar or []
        self.ner_count = ner_count or 0

        if uuid:
            self.get()

    def __str__(self, sanitized=True):
        """Convert the RSSItem to a string representation, optionally sanitizing the title and description."""
        if sanitized:
            sanitized_title = re.sub(r"[^A-Za-z0-9À-ÿ\s]", " ", self.title)
            sanitized_description = re.sub(r"[^A-Za-z0-9À-ÿ\s]", " ", self.description)
            return sanitized_title + " " + sanitized_description
        else:
            return self.title + " " + self.description


    def to_dict(self):
        """Convert the RSSItem to a dictionary format for API calls."""
        return {
            "uuid": self.uuid,
            "link": self.link,
            "title": self.title,
            "description": self.description,
            "pubDate": self.pubDate,
            "ogp": self.ogp,
            "image": self.image,
            "source": self.source,
            "categorie": self.categorie,
            "frontpage_id": self.frontpage_id if self.frontpage_id is not None else 0,
            "tags": self.tags,
            "embedding": self.embedding,
            "similar": self.similar,
            "ner_count": self.ner_count,
        }

    def from_dict(self, data):
        """Populate the RSSItem object from a dictionary (e.g., API response)."""
        self.uuid = data.get("uuid")
        self.link = data.get("link")
        self.title = data.get("title")
        self.description = data.get("description")
        self.pubDate = data.get("pubDate")
        self.ogp = data.get("ogp")
        self.image = data.get("image")
        self.source = data.get("source")
        self.categorie = data.get("categorie")
        self.frontpage_id = data.get("frontpage_id", 0)
        self.tags = data.get("tags", [])
        self.embedding = data.get("embedding", [])
        self.similar = data.get("similar", [])
        self.ner_count = data.get("ner_count", 0)

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
