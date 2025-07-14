#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Module Name: backend/app.py
Description: This module serves as the backend, hosting the API server.
It handles incoming requests for adding articles and prompts to the
database.

TODO: "The garbage collector for deleting articles >1000 is not implemented yet It should be triggered randomly during POST requests when adding new articles. Same for prompts based on last usage info.
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
    settings: Optional[list] = []


class PromptResponse(PromptCreate):
    uuid: str
    text: str
    text_improved: Optional[str]
    key:  Optional[str]
    tags:  Optional[list]
    created_at: Optional[datetime]
    lastused_at: Optional[datetime]
    embedding: Optional[list]
    feed: Optional[list]
    settings: Optional[list]
    ner_count: Optional[int]
    enable: Optional[bool]


# RSSItem Pydantic models
class RSSItemCreate(BaseModel):
    link: str
    title: str
    description: Optional[str] = None
    pubDate: Optional[datetime] = None
    ogp:  Optional[list] = None
    source: str
    categorie: str
    frontpage_id: int = 0


class RSSItemResponse(RSSItemCreate):
    uuid: str
    ner_count: int


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
                or_(
                    RSSItem.tags != "[]",
                    RSSItem.embedding != "[]",
                )
            )
            .order_by(RSSItem.pubDate.asc()) #return older first
            .all()
        )
    elif type == "prompts":
        items = (
            db.query(Prompt)
            .filter(
                or_(
                    Prompt.tags != "[]",
                    Prompt.embedding != "[]",
                )
            )
            .order_by(Prompt.created_at.desc())  #return recent first
            .all()
        )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid type. Use 'articles' or 'prompts'."
        )

    uuids = [item.uuid for item in items]
    return uuids


@app.get("/search/{uuid}")
def search(uuid: str, db: Session = Depends(get_db)):
    """
    Search articles that match a prompt.
    Args:
        uuid of a Prompt

    Returns:
        Return the list of articles.
    """
    db_item = (
        db.query(Prompt)
        .filter(
            Prompt.uuid == uuid,
            Prompt.embedding != [],
        )
        .first()
    )
    if db_item is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    #TO DO: Ajouter filtre sur setttings
    items = db.query(RSSItem).filter(RSSItem.embedding != "[]").order_by(RSSItem.pubDate.desc()).all()
    result = []
    score_1 = 0
    score_2 = 0
    for item in items:
        logging.info(f"Search score for article: {item.uuid}")
        if item.embedding and item.embedding != "[]":
            score_1 = utils.calculate_similarity(item.embedding, db_item.embedding)

        if item.tags and item.tags != "[]" and db_item.tags and db_item.tags != "[]":
            score_2 = utils.calculate_ner(item.tags, db_item.tags)

        total = score_1 + score_2
        if total > 0.9:
            result.append(
                {
                    "uuid": item.uuid,
                    "score": total
                }
            )
    return result


@app.get("/ner/{type}")
def get_items_for_ner(type: str, db: Session = Depends(get_db)):
    if type == "articles":
        items = (
            db.query(RSSItem)
            .filter(
                and_(
                    or_(
                        RSSItem.tags == "[]",
                        RSSItem.embedding == "[]",
                        RSSItem.ogp == "",
                        RSSItem.ogp == "[]",
                        RSSItem.ogp == '[{"title": "", "basic": [], "open_graph": [], "twitter": [], "other": []}]',
                    ),
                    # Max retry per item is 3
                    RSSItem.ner_count <= 3,
                )
            )
            .order_by(RSSItem.pubDate.asc())
            .limit(10)
            .all()
        )
    elif type == "prompts":
        items = (
            db.query(Prompt)
            .filter(
                and_(
                    or_(
                        Prompt.tags == "[]",
                        Prompt.embedding == "[]",
                    ),
                    # Max retry per item is 3
                    Prompt.ner_count <= 3,
                )
            )
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


# API Endpoints for Prompt (query)
@app.get("/prompt/{uuid}", response_model=PromptResponse)
def get_prompt(uuid: str, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.uuid == uuid).first()
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


@app.post("/prompt/", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    db_prompt = Prompt(
        uuid=secrets.token_hex(12),
        key=secrets.token_hex(4),
        text=prompt.text,
        settings=prompt.settings
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


@app.put("/prompt/{uuid}/{key}", response_model=PromptResponse)
def update_prompt(uuid: str, key:str, data: dict, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(and_(Prompt.uuid == uuid, Prompt.key == key)).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if "text" in data:
        db_prompt.text = data["text"]
        # Modifier prompt.text impose une réinitialisation des
        # colonnes ci-dessous.
        db_prompt.text_improved = ""
        db_prompt.tags = []
        db_prompt.embedding = []
        db_prompt.feed = []
        db_prompt.ner_count = 0
    if "settings" in data:
        # Modifier prompt.settings ne nécessite pas de réinitialisation,
        # car la prochaine exécution de feedmaker mettra à jour le filtre.
        db_prompt.settings = data["settings"]
    if "tags" in data:
        db_prompt.tags = data["tags"]
    if "embedding" in data:
        db_prompt.embedding = data["embedding"]
    if "feed" in data:
        db_prompt.feed = data["feed"]
    if "ner_count" in data:
        db_prompt.ner_count = data["ner_count"]
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
def create_rss_item(rss_item: RSSItemCreate, db: Session = Depends(get_db)):
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
    )
    db.add(new_rss_item)
    db.commit()
    db.refresh(new_rss_item)
    return new_rss_item


@app.put("/rss-item/{uuid}", response_model=RSSItemResponse)
def update_rss_item(uuid: str, data: dict, db: Session = Depends(get_db)):
    rss_item = db.query(RSSItem).filter(RSSItem.uuid == uuid).first()

    if not rss_item:
        raise HTTPException(status_code=404, detail="RSSItem not found")
    if "tags" in data:
        rss_item.tags = data["tags"]
    if "embedding" in data:
        rss_item.embedding = data["embedding"]
    if "ogp" in data:
        rss_item.ogp = [data["ogp"]]
        logging.info(f"OQP: {data["ogp"]}")
    if "similar" in data:
        rss_item.similar = data["similar"]
    if "ner_count" in data:
        rss_item.ner_count = data["ner_count"]
    if "image" in data:
        rss_item.image = data["image"]
    db.commit()
    db.refresh(rss_item)
    return rss_item


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
