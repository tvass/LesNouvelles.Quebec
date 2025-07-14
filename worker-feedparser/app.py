#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: worker-feedparser/app.py
Description: Application responsible for parsing RSS feeds and posting them to the API for storage in the database.
It handles different HTTP response codes, including:

- [200] Success: Article successfully added to the database.
- [409] Conflict: Article already exists in the database.
- [Other] HTTP Error: Displays the respective error code if any other issue occurs during the request.

"""

import os
import sys
import requests
from datetime import datetime, timedelta
import time
from html.parser import HTMLParser
import feedparser
import yaml
import json
import html
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../common")))

import utils
import rss_item
import prompt

# Setup logging configuration

def strip_html_tags(text):
    """Delete HTML tags from a string."""
    parser = MLStripper()
    parser.feed(text)
    return parser.get_data()


class MLStripper(HTMLParser):
    """Class to strip HTML tags from a string."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return "".join(self.text)


def insert_rss_feed(url, source_title, category):
    """Post a RSS feed item to the API."""
    feed = feedparser.parse(url)
    for entry in feed.entries:
        pubDate = (
            datetime(*entry.published_parsed[:6])
            if "published_parsed" in entry
            else datetime.utcnow()
        )
        # Ignore articles older than 48 hours
        if pubDate < datetime.utcnow() - timedelta(hours=48):
            logging.info("⏩ Item ignored - Older than 48 hours")
            continue

        item = rss_item.RSSItemClient(
            title=strip_html_tags(entry.get("title", "").strip()),
            link=entry.get("link", "").strip(),
            description=strip_html_tags(entry.get("description", "").strip()),
            pubDate=pubDate.isoformat(),
            source=source_title,
            categorie=category,
        )

        try:
            item.create()
        except Exception as e:
            logging.error(f"An error occurred while creating the item: {e}")
        time.sleep(2)


with open("source.yaml", "r", encoding="utf-8") as file:
    sources_data = yaml.safe_load(file)

while True:
    for source in sources_data["sources"]:
        logging.info(f"Processing source: {source}")
        for key, details in source.items():
            logging.info(f"Checking key: {key}")
            if "rss" in details:
                for rss in details["rss"]:
                    rss_url = rss["url"]
                    category = rss["category"]
                    logging.info(f"RSS URL: {rss_url} | Category: {category}")
                    insert_rss_feed(rss_url, details["title"], category)
            else:
                logging.info(f"No RSS found for {details['title']}")

            # Actually commented to be reimplemented later
            # if "frontpage" in details:
            #     for frontpage_rss in details["frontpage"]:
            #         logging.info(f"Frontpage RSS URL: {frontpage_rss} | Source: {details['title']}")
            #         set_frontpage(frontpage_rss, details["title"])

    time.sleep(300)
