#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/utils.py
Description:
"""

import requests
import config
from typing import List
import cohere
import os
import re
import logging
import numpy as np


def fetch_items(endpoint: str) -> List[str]:
    """
    Retrieves a list of items for NER and embedding processing.
    Args:
        endpoint (str): The API endpoint (e.g., 'articles', 'prompts').

    Returns:
        List[str]: A list of item IDs or an empty list on failure.
    """
    url = f"{config.LNQ_BASE_URL}/ner/{endpoint}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.json()  # Assuming the response is always a JSON list
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return []


def calculate_ner(a_tags, b_tags):
    """
    Calculates the number of common NER tags.
    Args:
        List of tags from 2 items.

    Returns:
        Return the similarity score.
    """
    a_tags = [tag["text"] for tag in a_tags]
    b_tags = [tag["text"] for tag in b_tags]
    return len(set(a_tags) & set(b_tags)) / len(set(a_tags))


def calculate_similarity(a_embedding, b_embedding):
    """
    Calculates the similarity between 2 items (whatever they are a prompt or an article).
    Args:
        Embeddings from two items.

    Returns:
        Return the similarity score.
    """
    a_embedding = np.array(a_embedding)
    b_embedding = np.array(b_embedding)
    return np.dot(a_embedding, b_embedding) / (
        np.linalg.norm(a_embedding) * np.linalg.norm(b_embedding)
    )
