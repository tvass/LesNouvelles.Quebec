#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name: frontend/app.py
Description: Web application utilizing Bootstrap for the frontend. Currently,
it has read-only access to the database but will have need transition to using the
backend API.
"""

import os
import pytz
import numpy as np
import requests

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_wtf import FlaskForm, CSRFProtect
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
import requests

montreal_tz = pytz.timezone("America/Toronto")

Base = declarative_base()
db_path = os.environ.get("LNQ_DB_PATH", os.path.join(os.getcwd(), "../db/news.db"))
if not os.path.exists(db_path):
    exit(f"Database file {db_path} not found.")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}?mode=ro"

# set default button sytle and size, will be overwritten by macro parameters
app.config["BOOTSTRAP_BTN_STYLE"] = "primary"
app.config["BOOTSTRAP_BTN_SIZE"] = "sm"

# set default icon title of table actions
app.config["BOOTSTRAP_TABLE_VIEW_TITLE"] = "Read"
app.config["BOOTSTRAP_TABLE_EDIT_TITLE"] = "Update"
app.config["BOOTSTRAP_TABLE_DELETE_TITLE"] = "Remove"
app.config["BOOTSTRAP_TABLE_NEW_TITLE"] = "Create"

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

ITEMS_PER_PAGE = 15

valid_categories = {
    "international": {"name": "International", "color": "#4a90e2"},
    "politique": {"name": "Politique", "color": "#e74c3c"},
    "nouvelle": {"name": "Nouvelles", "color": "#cc6699"},
    "economie": {"name": "Économie", "color": "#f39c12"},
    "science": {"name": "Science", "color": "#1abc9c"},
    "education": {"name": "Éducation", "color": "#3498db"},
    "justice": {"name": "Justice & Faits divers", "color": "#9b59b6"},
    "environnement": {"name": "Environnement", "color": "#2ecc71"},
    "sante": {"name": "Santé", "color": "#e91e63"},
    "sport": {"name": "Sports", "color": "#f39c12"},
    "art": {"name": "Art & Culture", "color": "#ff5722"},
    "societe": {"name": "Société", "color": "#2980b9"},
    "techno": {"name": "Techno", "color": "#34495e"},
    "transport": {"name": "Transport", "color": "#ce767c"},
    "alimentation": {"name": "Alimentation", "color": "#f1c40f"},
    "opinion": {"name": "Opinion", "color": "#ea66dc"},
}

valid_actions = [
    "create-prompt",
    "update-prompt"
]

def calculate_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def read_settings(data):
    text = data.get("prompt", "")
    settings = [{key: value} for key, value in data.items() if key not in ("csrf_token", "prompt")]
    return text, settings

class RSSItem(db.Model):
    __tablename__ = "rss_items"

    link = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pubDate = Column(DateTime, nullable=True)
    uuid = Column(Text(24), nullable=False)
    source = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    frontpage_id = Column(Integer, nullable=False)
    similar = Column(JSON, nullable=True, default=[])
    image = Column(Text, nullable=True)


class Prompt(db.Model):
    __tablename__ = "prompt"

    uuid = Column(Text(24), primary_key=True, index=True, nullable=False)
    text = Column(String, index=True)
    created_at = Column(DateTime, nullable=True)
    lastused_at = Column(DateTime, nullable=True)
    key = Column(Text(8), nullable=False)
    tags = Column(JSON, nullable=True, default=[])
    embedding = Column(JSON, nullable=True, default=[])
    feed = Column(JSON, nullable=True, default=[])

@app.route("/")
@app.route("/<categorie>")
def index(categorie=None):
    if categorie and categorie not in valid_categories:
        categorie = None

    page = request.args.get("page", 1, type=int)

    query = RSSItem.query
    if categorie:
        query = query.filter(RSSItem.categorie.in_([categorie]))
    pagination = query.order_by(RSSItem.pubDate.desc()).paginate(
        page=page, per_page=ITEMS_PER_PAGE, error_out=False
    )
    rss_items = pagination.items

    data = []
    now = datetime.now(montreal_tz)

    for item in rss_items:
        pubDate = pytz.utc.localize(item.pubDate).astimezone(montreal_tz)
        days_ago = (now.date() - pubDate.date()).days

        time_str = f"{pubDate.strftime('%H:%M')} {pubDate.strftime('%d-%m')}"

        data.append(
            {
                "source": item.source,
                "title": item.title,
                "description": item.description,
                "link": item.link,
                "pubDate": time_str,
                "uuid": item.uuid,
                "categorie": item.categorie,
                "similar": item.similar,
                "image": item.image
            }
        )

    return render_template(
        "home.html",
        #rss_items=rss_items,
        data=data,
        pagination=pagination,
        selected_category=categorie,
        valid_categories=valid_categories,
    )

@app.route("/prompt/", defaults={"uuid": None, "key": None})
@app.route("/prompt/<uuid>", defaults={"key": None})
@app.route("/prompt/<uuid>/<key>")
def prompt(uuid=None, key=None):
    data = []
    _key= None
    _uuid = None
    prompt = None
    pagination = None
    page = request.args.get("page", 1, type=int)

    query = Prompt.query
    if uuid:
        query = query.filter(Prompt.uuid == uuid)
        if key:
            query = query.filter(Prompt.key == key)
        prompt = query.first()

    if prompt is not None:
        _uuid = uuid
        if key is not None:
            _key = key

        if prompt.feed == []:
            data={}
        else:
            query = RSSItem.query
            if prompt and prompt.feed:
                uuids = [item["uuid"] for item in prompt.feed]
                query = query.filter(RSSItem.uuid.in_(uuids))

            pagination = query.order_by(RSSItem.pubDate.desc()).paginate(
                page=page, per_page=ITEMS_PER_PAGE, error_out=False
            )
            rss_items = pagination.items
            now = datetime.now(montreal_tz)

            for item in rss_items:
                score = next((feed_item["score"] for feed_item in prompt.feed if feed_item["uuid"] == item.uuid), None)
                pubDate = pytz.utc.localize(item.pubDate).astimezone(montreal_tz)
                days_ago = (now.date() - pubDate.date()).days

                time_str = f"{pubDate.strftime('%H:%M')} {pubDate.strftime('%d-%m')}"

                data.append(
                    {
                        "source": item.source,
                        "title": item.title,
                        "description": item.description,
                        "image": item.image,
                        "link": item.link,
                        "pubDate": time_str,
                        "uuid": item.uuid,
                        "categorie": item.categorie,
                        "similar": item.similar,
                        # Add score from prompt.feed
                        "score": score,
                    }
                )

    return render_template(
        "prompt.html",
        data=data,
        selected_category="prompt",
        valid_categories=valid_categories,
        pagination=pagination,
        uuid=_uuid,
        prompt=prompt,
        key=_key,
    )


@app.route("/detail/<uuid>")
def detail(uuid=None):
    query = RSSItem.query
    if uuid:
        query = query.filter(RSSItem.uuid == uuid)
    rss_item = query.first()
    if not rss_item:
        return "Item not found", 404
    pubDate = pytz.utc.localize(rss_item.pubDate).astimezone(montreal_tz)
    data = {
        "source": rss_item.source,
        "title": rss_item.title,
        "description": rss_item.description,
        "link": rss_item.link,
        "pubDate": pubDate,
        "uuid": rss_item.uuid,
        "categorie": rss_item.categorie,
        "similar": None
    }
    return render_template("detail.html", data=data, valid_categories=valid_categories)


@app.route("/unes")
def unes():
    query = RSSItem.query.filter(RSSItem.frontpage_id > 0)
    rss_items = query.order_by(RSSItem.frontpage_id.asc(), RSSItem.pubDate.desc()).all()

    data = []
    now = datetime.now(montreal_tz)

    for item in rss_items:
        pubDate = pytz.utc.localize(item.pubDate).astimezone(montreal_tz)
        days_ago = (now.date() - pubDate.date()).days
        time_str = f"{pubDate.strftime('%H:%M')} {pubDate.strftime('%d-%m')}"
        data.append(
            {
                "source": item.source,
                "title": item.title,
                "description": item.description,
                "link": item.link,
                "pubDate": time_str,
                "uuid": item.uuid,
                "categorie": item.categorie,
            }
        )

    return render_template(
        "unes.html",
        rss_items=rss_items,
        data=data,
        selected_category="unes",
        valid_categories=valid_categories,
    )


@app.route("/post/<action>", methods=["POST"], strict_slashes=False)
def handle_post(action=None):
    if action and action not in valid_actions:
        flash("Invalid action", "danger")
        return redirect("/not-welcome")

    data = request.form
    text, settings = read_settings(data)

    if action == "create-prompt":
        try:
            response = requests.post(
                    "http://127.0.0.1:8000/prompt/", json={"text": text, "settings": settings}
                )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            flash(f"Error: {e}", "danger")
            return redirect("/error")
        if response.status_code != 200:
            flash(f"Error: Code HTTP is {response.status_code}", "danger")
            return redirect("/error")

    if action == "update-prompt":
        try:
            response = requests.put(
                "http://127.0.0.1:8000/prompt/"
                + str(request.form["uuid"])
                + "/"
                + str(request.form["key"]),
                json={
                    "text": text,
                    "settings": settings,
                },
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            flash(f"Error: {e}", "danger")
            return redirect("/error")
        if response.status_code != 200:
            flash(f"Error: Code HTTP is {response.status_code}", "danger")
            return redirect("/error")

    return render_template(
        "welcome.html",
        valid_categories=valid_categories,
        code=response.status_code,
        response=response.json(),
        data=data
    )


@app.route("/a-propos", strict_slashes=False)
def a_propos():
    return render_template("a-propos.html", valid_categories=valid_categories)


@app.route("/not-welcome", strict_slashes=False)
def not_welcome():
    return render_template("not-welcome.html", valid_categories=valid_categories)


@app.route("/error", strict_slashes=False)
def error():
    return render_template("error.html", valid_categories=valid_categories)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
