#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/models.py
Description: Defines the RSSItem and Prompt classes for database
interactions and low-level processing.
"""

from sqlalchemy import create_engine, Column, Text, String, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON
from datetime import datetime
import numpy as np
import base64

Base = declarative_base()


class Prompt(Base):
    __tablename__ = "prompt"

    uuid = Column(Text(24), primary_key=True, index=True, nullable=False)
    text = Column(String)
    text_improved = Column(
        String,
        nullable=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    lastused_at = Column(DateTime, default=datetime.utcnow)
    key = Column(Text(8), nullable=False)
    tags = Column(JSON, nullable=True, default=[])
    embedding = Column(JSON, nullable=True, default=[])
    feed = Column(JSON, nullable=True, default=[])
    settings = Column(JSON, nullable=True, default=[])
    ner_count = Column(Integer, nullable=True, default=0)
    enable = Column(Boolean, nullable=True, default=True)


    def __init__(
        self,
        uuid,
        text,
        key,
        text_improved=None,
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
        self.text_improved = text_improved or None
        self.key = key
        self.tags = tags or []
        self.created_at = created_at or datetime.utcnow()
        self.lastused_at = lastused_at or datetime.utcnow()
        self.embedding = embedding or []
        self.feed = feed or []
        self.settings = settings or []
        self.ner_count = ner_count or 0
        self.enable = enable or True


class RSSItem(Base):
    __tablename__ = "rss_items"

    uuid = Column(Text(24), primary_key=True, index=True, nullable=False)
    link = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pubDate = Column(DateTime, nullable=False)
    ogp = Column(JSON, nullable=True, default=[])
    image = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    frontpage_id = Column(Integer, nullable=True, default=0)
    tags = Column(JSON, nullable=True, default=[])
    embedding = Column(JSON, nullable=True, default=[])
    similar = Column(JSON, nullable=True, default=[])
    ner_count = Column(Integer, nullable=True, default=0)


    def __init__(
        self,
        uuid,
        link,
        title,
        source,
        categorie,
        pubDate,
        ogp=None,
        image=None,
        frontpage_id=None,
        tags=None,
        description=None,
        embedding=None,
        similar=None,
        ner_count=None,
    ):
        self.uuid = uuid
        self.link = link
        self.title = title
        self.source = source
        self.categorie = categorie
        self.pubDate = pubDate
        self.ogp = ogp or []
        self.image = image
        self.frontpage_id = frontpage_id if frontpage_id is not None else 0
        self.tags = tags or []
        self.description = description
        self.embedding = embedding or []
        self.similar = similar or []
        self.ner_count = ner_count or 0


    def set_image(self, image_binary):
        self.image = base64.b64encode(image_binary).decode('utf-8')
