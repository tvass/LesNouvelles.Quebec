#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: worker-ner/app.py
Description: A worker that performs Named Entity Recognition (NER)
and computes embeddings for articles and prompts.
"""

# Standard library imports
import base64
import cv2
import os
import sys
import logging
import time
import json
import re

# Third-party imports
import requests
import numpy as np
import torch

# from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
from dataclasses import asdict
from PIL import Image, ImageDraw, ImageFont


# Local application imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../common")))
import utils
import rss_item
import prompt
from config import *
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    pipeline,
    CamembertTokenizer,
)


from meta_tags_parser import parse_meta_tags_from_source, structs
from bs4 import BeautifulSoup

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_THREAD_LIMIT"] = "1"

# Load the model and tokenizer once
TOKENIZER = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
MODEL = AutoModelForTokenClassification.from_pretrained(
    "Jean-Baptiste/camembert-ner"
)
MODEL = MODEL.to("cpu")
NLP = pipeline("ner", model=MODEL, tokenizer=TOKENIZER, device=-1)

def get_ogp(link):
    """Fetch Open Graph Protocol (OGP) metadata from the given link."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        html_content = response.text
        # Using bs4 allows you to set the User-Agent and properly format the HTML
        # parse_meta_tags_from_source fails to detect all meta tags without this.
        soup = BeautifulSoup(response.text, "html.parser")
        formatted_html = soup.prettify()
        ogp: structs.TagsGroup = parse_meta_tags_from_source(formatted_html)
        ogp_dict = asdict(ogp)
        return ogp_dict
    except requests.RequestException as e:
        logging.error(f"Error fetching OGP data: {e}")
        return {}


def get_image(data, banner_text="© Image Source"):
    try:
        open_graph = data.get("open_graph", [])
        for entry in open_graph:
            if isinstance(entry, dict) and entry.get("name") == "image":
                image_url = entry.get("value")
                if image_url:
                    response = requests.get(image_url)
                    response.raise_for_status()

                    # Convert image bytes to OpenCV format
                    image_array = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                    if image is None:
                        print("Error: Unable to decode image.")
                        return None

                    # Resize image to a width of 800px while maintaining aspect ratio
                    width = 800
                    height = int((width / image.shape[1]) * image.shape[0])
                    resized_image = cv2.resize(image, (width, height))

                    # Add a black 50px line at the bottom of the image
                    black_line = np.zeros((50, width, 3), dtype=np.uint8)
                    resized_image_with_line = np.vstack((resized_image, black_line))

                    # Convert to PIL Image to use with Pillow
                    pil_image = Image.fromarray(
                        cv2.cvtColor(resized_image_with_line, cv2.COLOR_BGR2RGB)
                    )

                    # Create an ImageDraw object
                    draw = ImageDraw.Draw(pil_image)

                    # Set the font path (make sure you have the font available)
                    font = ImageFont.truetype(
                        "fonts/VictorMono-Bold.ttf",
                        40,
                    )

                    # Use textbbox to get text width and height
                    bbox = draw.textbbox((0, 0), banner_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    # Position the text at the bottom-left corner of the black line
                    text_x = 10  # Padding from the left
                    padding_bottom = 20  # Padding from the bottom
                    text_y = (
                        resized_image_with_line.shape[0] - text_height - padding_bottom
                    )

                    # Draw the text on top of the black line
                    draw.text(
                        (text_x, text_y),
                        banner_text,
                        font=font,
                        fill=(255, 255, 255),  # White text
                    )

                    # Convert back to OpenCV format
                    image_with_text = cv2.cvtColor(
                        np.array(pil_image), cv2.COLOR_RGB2BGR
                    )

                    # Encode updated image to base64
                    _, buffer = cv2.imencode(".jpg", image_with_text)
                    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode()}"

    except Exception as e:
        print(f"Error occurred: {e}")

    return None


def get_ner_and_embedding(text):
    """Get both NER tags and embeddings for the given text."""

    tokenizer = TOKENIZER
    model = MODEL
    nlp_ner = NLP

    ner_results = nlp_ner(text)

    # Format NER results
    formatted_results = [
        {"entity": result["word"].lstrip("▁"), "label": result["entity"]}
        for result in ner_results
    ]

    # Tokenize the input text for embeddings
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    inputs = {key: value.to("cpu") for key, value in inputs.items()}

    # Run the model to get hidden states (for embeddings)
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    # Access the hidden states (get the last layer hidden states)
    hidden_states = outputs.hidden_states
    last_hidden_state = hidden_states[-1]  # Last hidden state layer

    # Calculate embeddings by averaging across all tokens
    embeddings = last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy()

    return formatted_results, embeddings.tolist()


def process_item(item):
    """Process NER and Embedding for articles or prompts."""
    logging.info(f"[{item.uuid}]: EMB and NER")
    ner_tags, embeddings = get_ner_and_embedding(item.__str__())
    item.tags = ner_tags
    item.embedding = embeddings
    if hasattr(item, 'ogp'):
        logging.info(f"[{item.uuid}]: OGP")
        ogp = get_ogp(item.link)
        item.ogp = ogp
    if hasattr(item, 'image'):
        logging.info(f"[{item.uuid}]: Save image")
        item.image = get_image(item.ogp, "© " + item.source + " " + str(time.localtime().tm_year))
    item.ner_count += 1
    logging.info(f"[{item.uuid}]: Update")
    try:
        item.update()
    except Exception as e:
        logging.error(f"[{item.uuid}]: Error to update: {e}")

def main():
    while True:
        for item_type in ["prompts", "articles"]:
            try:
                items = utils.fetch_items_no_ner(item_type)
                logging.info(f"Next 10 {item_type} to work on: {items}")
            except Exception as e:
                logging.error(f"Error fetching {item_type}: {e}")
                continue

            for item_uuid in items:
                item = (
                    rss_item.RSSItemClient(uuid=item_uuid)
                    if item_type == "articles"
                    else prompt.PromptClient(uuid=item_uuid)
                )
                process_item(item)
                time.sleep(2)
        time.sleep(2)


if __name__ == "__main__":
    main()
