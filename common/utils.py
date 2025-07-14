#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/utils.py
Description:
"""

import requests
import config
from typing import List
import os
import re
import logging
import numpy as np


def fetch_all(endpoint: str) -> List[str]:
    """
    Retrieves all items.
    Args:
         endpoint (str): The API endpoint (e.g., 'articles', 'prompts').
    Returns:
    List[str]: A list of item IDs or an empty list on failure.
    """
    url = f"{config.LNQ_BASE_URL}/all/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

def fetch_items_no_ner(endpoint: str) -> List[str]:
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


def fetch_items_no_similar() -> List[str]:
    """
    Retrieves a list of articles for SIMILAR processing.
    Args:

    Returns:
        List[str]: A list of item IDs or an empty list on failure.
    """
    url = f"{config.LNQ_BASE_URL}/similar"

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
    a_entities = [tag["entity"] for tag in a_tags]
    b_entities = [tag["entity"] for tag in b_tags]

    # Calculate the similarity score based on the common entities
    return len(set(a_entities) & set(b_entities)) / len(set(a_entities))

def calculate_similarity(a_embedding, b_embedding):
    """
    Calculates the similarity between 2 items (whatever they are a prompt or an article).
    Args:
        Embeddings from two items.

    Returns:
        Return the similarity score.
    """
    a_embedding = np.array(a_embedding)
    try:
        b_embedding = np.array(b_embedding)
        return np.dot(a_embedding, b_embedding) / (
            np.linalg.norm(a_embedding) * np.linalg.norm(b_embedding)
        )
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0
