#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: worker-feedmaker/app.py
Description: This script should apply cosine similarityto create a custom feed.

For the record, expected workflow:

1. Text Preprocessing:
- Tokenize text, normalize by converting to lowercase, and remove unnecessary characters.
- Lemmatize the words to get the root form (e.g., "courir" instead of "courrait").
- Remove stop words (common words like "the", "a", "of" which don't add value for topic identification).

2. Named Entity Recognition (NER):
- Extract entities such as team names, location, date, political figures, and organizations.

3. Text Classification:
- Use a text classification model (e.g., fine-tuned BERT, XLM-Roberta, or GPT models) to classify the text into
  different predefined categories (e.g., sports, politics, etc.).
- These models can be fine-tuned on your own dataset, with labeled articles for each category.

4. Semantic Search:
- Convert the user's query and news articles into embeddings using a pre-trained transformer-based model like
  BERT, Sentence-BERT, or distilBERT.
- Calculate similarity using cosine similarity, which will provide a relevance score.

5. Ranking:
- Rank articles based on their similarity to the query. More relevant articles will have higher similarity scores.
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


while True:
    time.sleep(5)
    try:
        prompts = utils.fetch_all("prompts")
        logging.info(f"📄 Get all: {prompts}")
    except Exception as e:
        logging.error(f"Error fetching prompts: {e}")
        continue
    for uuid in prompts:
        time.sleep(5)
        try:
            my_prompt = prompt.PromptClient(uuid)
            my_prompt.search()
            my_prompt.update()
        except Exception as e:
            logging.error(f"Error fetching articles: {e}")
        continue
