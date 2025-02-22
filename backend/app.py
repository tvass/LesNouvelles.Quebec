#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Module Name: backend/app.py
Description: This module serves as the backend, hosting the API server.
It handles incoming requests for adding articles and prompts to the
database. The garbage collector for deleting articles >1000 is not
implemented yet. It should be triggered randomly during POST requests
when adding new articles. Same for prompts based on last usage info.
"""

import os
import secrets
import sys
import uvicorn
import numpy as np
from typing import List, Dict, Optional
import dotenv

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    Integer,
    JSON,
    or_,
    and_,
    func,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../common")))
from models import Base, Prompt, RSSItem
import utils

# Create DB files and tables
db_path = os.getenv("LNQ_DB_PATH", os.path.join(os.getcwd(), "db/news.db"))
os.makedirs(os.path.dirname(db_path), exist_ok=True)
if not os.path.exists(db_path):
    open(db_path, "w").close()
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


# FastAPI app instance
app = FastAPI()


# Prompt Pydantic models
# This will serve as the default schema when creating items via the API
class PromptCreate(BaseModel):
    text: str
    tags: Optional[List] = []
    embedding: Optional[List] = []


class PromptResponse(PromptCreate):
    uuid: str
    key: str
    created_at: datetime

    class Config:
        from_attributes = True


# RSSItem Pydantic models
class RSSItemCreate(BaseModel):
    link: str
    title: str
    description: Optional[str] = None
    pubDate: Optional[datetime] = None
    source: str
    categorie: str
    frontpage_id: int = 0
    tags: Optional[List] = []
    embedding: Optional[List] = []


class RSSItemResponse(RSSItemCreate):
    uuid: str

    class Config:
        from_attributes = True


# Dependency to get the database session
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# Returns all items in the database that have tags AND embeddings
@app.get("/all/{type}")
def get_all(type: str, db: Session = Depends(get_db)):
    if type == "articles":
        items = (
            db.query(RSSItem)
            .filter(
                and_(
                    RSSItem.tags != "[]",
                    RSSItem.embedding != "[]",
                )
            )
            .order_by(RSSItem.pubDate.asc())
            .all()
        )
    elif type == "prompts":
        items = (
            db.query(Prompt)
            .filter(
                and_(
                    Prompt.tags != "[]",
                    Prompt.embedding != "[]",
                )
            )
            .order_by(Prompt.created_at.asc())
            .all()
        )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid type. Use 'articles' or 'prompts'."
        )

    uuids = [item.uuid for item in items]
    return uuids


# Returns articles that are similar to a given {prompt} or {articles} uuid
# Endpoint for testing only as it will done in the background (worker-feedmaker)
@app.get("/vector/{type}/{uuid}")
@app.get("/vector/{type}/{uuid}/{limit}")
def get_vector(type: str, uuid: str, limit: int = 3, db: Session = Depends(get_db)):
    model = RSSItem if type == "articles" else Prompt if type == "prompts" else None
    if not model:
        raise HTTPException(status_code=400, detail="Invalid type")

    db_item = (
        db.query(model)
        .filter(
            model.uuid == uuid,
            model.tags_embedding != [],
            model.embedding != [],
        )
        .first()
    )
    if db_item is None:
        raise HTTPException(status_code=404, detail="Article not found")
    items = db.query(RSSItem).filter(RSSItem.uuid != uuid).all()
    result = []
    for item in items:
        if item.embedding and item.embedding != "[]":
            logging.info(f"Article: {item.title} {item.uuid}")

            # Calculate score
            score_1 = utils.calculate_similarity(
                item.tags_embedding, db_item.tags_embedding
            )
            score_2 = utils.calculate_similarity(item.embedding, db_item.embedding)

            score_3 = utils.calculate_ner(item.tags, db_item.tags)

            total = score_1 + score_2 + score_3
            logging.info(f"Total: {score_1}, {score_2}, {score_3}: {total}")
            result.append(
                (
                    item.title,
                    item.uuid,
                    item.source,
                    f"score_1: {score_1}",
                    f"score_2: {score_2}",
                    f"score_3: {score_3}",
                    total,
                )
            )

    result = sorted(result, key=lambda x: x[6], reverse=True)
    return result[:limit]


@app.get("/ner/{type}")
def get_items_for_ner(type: str, db: Session = Depends(get_db)):
    if type == "articles":
        items = (
            db.query(RSSItem)
            .filter(
                or_(
                    RSSItem.tags == "[]",
                )
            )
            .order_by(RSSItem.pubDate.asc())
            .limit(10)
            .all()
        )
    elif type == "prompts":
        items = (
            db.query(Prompt)
            .filter(Prompt.tags == "[]")
            .order_by(Prompt.created_at.asc())
            .limit(10)
            .all()
        )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid type. Use 'articles' or 'prompts'."
        )

    uuids = [item.uuid for item in items]
    return uuids


# API Endpoints for Prompt
# Get a specific prompt by ID
@app.get("/prompt/{uuid}", response_model=PromptResponse)
def read_prompt(uuid: str, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.uuid == uuid).first()
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


@app.post("/prompt/", response_model=PromptResponse)
def create_new_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    db_prompt = Prompt(
        uuid=secrets.token_hex(12),
        key=secrets.token_hex(4),
        text=prompt.text,
        tags=prompt.tags,
        embedding=prompt.embedding,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


@app.put("/prompt/{uuid}", response_model=PromptResponse)
def update_prompt_tags(uuid: str, tag_update: dict, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.uuid == uuid).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if "tags" in tag_update:
        db_prompt.tags = tag_update["tags"]  # Update the tags column
    if "embedding" in tag_update:
        db_prompt.embedding = tag_update["embedding"]
    if "tags_embedding" in tag_update:
        db_prompt.tags_embedding = tag_update["tags_embedding"]
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


# API Endpoints for RSSItem (articles)
@app.get("/rss-item/{uuid}", response_model=RSSItemResponse)
def get_rss_item(uuid: str, db: Session = Depends(get_db)):
    rss_item = db.query(RSSItem).filter(RSSItem.uuid == uuid).first()
    if rss_item is None:
        raise HTTPException(status_code=404, detail="RSSItem not found")
    return rss_item


@app.post("/rss-item/", response_model=RSSItemResponse)
def create_new_rss_item(rss_item: RSSItemCreate, db: Session = Depends(get_db)):
    existing_rss_item = db.query(RSSItem).filter_by(link=rss_item.link).first()
    if existing_rss_item:
        raise HTTPException(
            status_code=409, detail="RSSItem with this link already exists"
        )
    new_rss_item = RSSItem(
        link=rss_item.link,
        title=rss_item.title,
        description=rss_item.description,
        pubDate=rss_item.pubDate,
        uuid=secrets.token_hex(12),
        source=rss_item.source,
        categorie=rss_item.categorie,
        frontpage_id=rss_item.frontpage_id,
        tags=rss_item.tags,
        embedding=rss_item.embedding,
    )
    db.add(new_rss_item)
    db.commit()
    db.refresh(new_rss_item)
    return new_rss_item


@app.put("/rss-item/{uuid}", response_model=RSSItemResponse)
def update_ner_tags(uuid: str, tag_update: dict, db: Session = Depends(get_db)):
    rss_item = db.query(RSSItem).filter(RSSItem.uuid == uuid).first()

    if not rss_item:
        raise HTTPException(status_code=404, detail="RSSItem not found")
    if "tags" in tag_update:
        rss_item.tags = tag_update["tags"]
    if "embedding" in tag_update:
        rss_item.embedding = tag_update["embedding"]
    if "tags_embedding" in tag_update:
        rss_item.tags_embedding = tag_update["tags_embedding"]
    db.commit()
    db.refresh(rss_item)
    return rss_item


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
