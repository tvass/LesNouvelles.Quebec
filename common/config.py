#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/config.py
Description: Load variables from the environment and provide default values.
"""


from dotenv import load_dotenv
import os

load_dotenv()

LNQ_API_URL = os.getenv("LNQ_API_URL", "http://127.0.0.1")
LNQ_API_PORT = os.getenv("LNQ_API_PORT", "8000")
LNQ_BASE_URL = f"{LNQ_API_URL}:{LNQ_API_PORT}"
CO_API_KEY = os.getenv("CO_API_KEY", "NO_API_KEY")
LNQ_CONFIG_PATH = os.getenv(
    "LNQ_CONFIG_PATH", "/home/thomas/Documents/work/LesNouvelles.Quebec/config/"
)
