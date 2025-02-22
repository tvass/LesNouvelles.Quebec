#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: worker-ner/app.py
Description: A worker that performs Named Entity Recognition (NER)
and computes embeddings for articles and prompts.
"""

import logging
import sys
import os
import requests
import time
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../common")))

import utils
import rss_item
import prompt


def process_item(item, item_type):
    """Process NER and Embedding for articles or prompts."""
    if not item.tags:
        logging.info(f"✅ [{item.uuid}] Starting NER for {item_type}")
        try:
            item.get_ner()
        except Exception as e:
            logging.error(f"Error during NER for {item_type} [{item.uuid}]: {e}")
            return

    if not item.embedding:
        logging.info(f"✅ [{item.uuid}] Starting EMB for {item_type}")
        try:
            item.get_embedding()
        except Exception as e:
            logging.error(f"Error during EMB for {item_type} [{item.uuid}]: {e}")
            return

    if not item.tags_embedding:
        logging.info(f"✅ [{item.uuid}] Starting EMB for {item_type}")
        try:
            item.get_tags_embedding()
        except Exception as e:
            logging.error(f"Error during EMB for {item_type} [{item.uuid}]: {e}")
            return

    logging.info(f"{item_type} EMB tags: {item.embedding}")

    try:
        item.update()
    except Exception as e:
        logging.error(f"Error while updating {item_type} [{item.uuid}]: {e}")


while True:
    for item_type in ["prompts", "articles"]:
        try:
            items = utils.fetch_items(item_type)
            logging.info(f"📄 Next 10 {item_type} to work on: {items}")
        except Exception as e:
            logging.error(f"Error fetching {item_type}: {e}")
            continue

        for item_uuid in items:
            item = (
                rss_item.RSSItemClient(uuid=item_uuid)
                if item_type == "articles"
                else prompt.PromptClient(uuid=item_uuid)
            )

            process_item(item, item_type)

    time.sleep(5)
