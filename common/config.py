#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/config.py
Description: Load variables from the environment and provide default values.
"""


from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

LNQ_API_URL = os.getenv("LNQ_API_URL", "http://127.0.0.1")
LNQ_API_PORT = os.getenv("LNQ_API_PORT", "8000")
LNQ_BASE_URL = f"{LNQ_API_URL}:{LNQ_API_PORT}"
LNQ_MODEL = os.getenv("LNQ_MODEL", "cohere")
LNQ_CONFIG_PATH = os.getenv(
    "LNQ_CONFIG_PATH", "/home/thomas/Documents/work/LesNouvelles.Quebec/config/"
)
