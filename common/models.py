#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: common/models.py
Description: RSSItem(Base) and Prompt(Base) classes for interacting
with the database.
"""

from sqlalchemy import create_engine, Column, Text, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON
from datetime import datetime
import numpy as np

Base = declarative_base()


class Prompt(Base):
    __tablename__ = "prompt"

    uuid = Column(Text(24), primary_key=True, index=True, nullable=False)
    text = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lastused_at = Column(DateTime, default=datetime.utcnow)
    key = Column(Text(8), nullable=False)
    tags = Column(JSON, nullable=True, default=[])
    embedding = Column(JSON, nullable=True, default=[])
    tags_embedding = Column(
        JSON, nullable=True, default=[]
    )  # New column for tags embedding

    def __init__(
        self,
        uuid,
        text,
        key,
        tags=None,
        created_at=None,
        lastused_at=None,
        embedding=None,
        tags_embedding=None,
    ):
        self.uuid = uuid
        self.text = text
        self.key = key
        self.tags = tags or []
        self.created_at = created_at or datetime.utcnow()
        self.lastused_at = lastused_at or datetime.utcnow()
        self.embedding = embedding or []
        self.tags_embedding = tags_embedding or []

    def set_embedding(self, embedding_vector):
        self.embedding = (
            embedding_vector.tolist()
            if isinstance(embedding_vector, np.ndarray)
            else embedding_vector
        )

    def get_embedding(self):
        return np.array(self.embedding) if self.embedding else None

    def set_tags_embedding(self, tags_embedding_vector):
        self.tags_embedding = (
            tags_embedding_vector.tolist()
            if isinstance(tags_embedding_vector, np.ndarray)
            else tags_embedding_vector
        )

    def get_tags_embedding(self):
        return np.array(self.tags_embedding) if self.tags_embedding else None


class RSSItem(Base):
    __tablename__ = "rss_items"

    uuid = Column(Text(24), primary_key=True, index=True, nullable=False)
    link = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pubDate = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    frontpage_id = Column(Integer, nullable=True, default=0)
    tags = Column(JSON, nullable=True, default=[])
    embedding = Column(JSON, nullable=True, default=[])
    tags_embedding = Column(
        JSON, nullable=True, default=[]
    )  # New column for tags embedding

    def __init__(
        self,
        uuid,
        link,
        title,
        source,
        categorie,
        pubDate,
        frontpage_id=None,
        tags=None,
        description=None,
        embedding=None,
        tags_embedding=None,
    ):
        self.uuid = uuid
        self.link = link
        self.title = title
        self.source = source
        self.categorie = categorie
        self.tags = tags or []
        self.description = description
        self.pubDate = pubDate
        self.frontpage_id = frontpage_id if frontpage_id is not None else 0
        self.embedding = embedding or []
        self.tags_embedding = tags_embedding or []

    def set_embedding(self, embedding_vector):
        self.embedding = (
            embedding_vector.tolist()
            if isinstance(embedding_vector, np.ndarray)
            else embedding_vector
        )

    def get_embedding(self):
        return np.array(self.embedding) if self.embedding else None

    def set_tags_embedding(self, tags_embedding_vector):
        self.tags_embedding = (
            tags_embedding_vector.tolist()
            if isinstance(tags_embedding_vector, np.ndarray)
            else tags_embedding_vector
        )

    def get_tags_embedding(self):
        return np.array(self.tags_embedding) if self.tags_embedding else None
