# -*- coding: utf-8 -*-
import os
import pytz

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_wtf import FlaskForm, CSRFProtect
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

montreal_tz = pytz.timezone('America/Toronto')

Base = declarative_base()
db_path = os.path.join(os.getcwd(), '/db/news.db')
if not os.path.exists(db_path):
    exit(f"Database file {db_path} not found.")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?mode=ro'

# set default button sytle and size, will be overwritten by macro parameters
app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

# set default icon title of table actions
app.config['BOOTSTRAP_TABLE_VIEW_TITLE'] = 'Read'
app.config['BOOTSTRAP_TABLE_EDIT_TITLE'] = 'Update'
app.config['BOOTSTRAP_TABLE_DELETE_TITLE'] = 'Remove'
app.config['BOOTSTRAP_TABLE_NEW_TITLE'] = 'Create'

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

ITEMS_PER_PAGE=50

valid_categories = {
    'international': {'name': 'International', 'color': '#4a90e2'},
    'politique': {'name': 'Politique', 'color': '#e74c3c'},
    'nouvelle': {'name': 'Nouvelles', 'color': '#cc6699'},
    'economie': {'name': 'Économie', 'color': '#f39c12'},
    'science': {'name': 'Science', 'color': '#1abc9c'},
    'education': {'name': 'Éducation', 'color': '#3498db'},
    'justice': {'name': 'Justice & Faits divers', 'color': '#9b59b6'},
    'environnement': {'name': 'Environnement', 'color': '#2ecc71'},
    'sante': {'name': 'Santé', 'color': '#e91e63'},
    'sport': {'name': 'Sports', 'color': '#f39c12'},
    'art': {'name': 'Art & Culture', 'color': '#ff5722'},
    'societe': {'name': 'Société', 'color': '#2980b9'},
    'techno': {'name': 'Techno', 'color': '#34495e'},
    'transport': {'name': 'Transport', 'color': '#ce767c'},
    'alimentation': {'name': 'Alimentation', 'color': '#f1c40f'},
    'opinion': {'name': 'Opinion', 'color': '#ea66dc'}
}

class RSSItem(db.Model):
    __tablename__ = 'rss_items'

    link = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pubDate = Column(DateTime, nullable=True)
    uuid = Column(Text(24), nullable=False)
    source = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    frontpage_id = Column(Integer, nullable=False)

@app.route('/')
@app.route('/<categorie>')
def index(categorie=None):
    if categorie and categorie not in valid_categories:
        categorie=None

    page = request.args.get('page', 1, type=int)

    query = RSSItem.query
    if categorie:
        query = query.filter(RSSItem.categorie.in_([categorie]))
    pagination = query.order_by(RSSItem.pubDate.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)
    rss_items = pagination.items

    data = []
    now = datetime.now(montreal_tz)

    for item in rss_items:
        pubDate = pytz.utc.localize(item.pubDate).astimezone(montreal_tz)
        days_ago = (now.date() - pubDate.date()).days

        time_str = f"{pubDate.strftime('%H:%M')}"

        data.append({
            'source': item.source,
            'title': item.title,
            'description': item.description,
            'link': item.link,
            'pubDate': time_str,
            'uuid': item.uuid,
            'categorie': item.categorie
        })

    return render_template('home.html', rss_items=rss_items, data=data, pagination=pagination, selected_category=categorie, valid_categories=valid_categories)

@app.route('/detail/<uuid>')
def detail(uuid=None):
    query = RSSItem.query
    if uuid:
        query = query.filter(RSSItem.uuid == uuid)
    rss_item = query.first()
    if not rss_item:
        return "Item not found", 404
    pubDate = pytz.utc.localize(rss_item.pubDate).astimezone(montreal_tz)
    data = {
        'source': rss_item.source,
        'title': rss_item.title,
        'description': rss_item.description,
        'link': rss_item.link,
        'pubDate': pubDate,
        'uuid': rss_item.uuid,
        'categorie': rss_item.categorie
    }
    return render_template('detail.html', data=data)


@app.route('/unes')
def unes():
    query = RSSItem.query.filter(RSSItem.frontpage_id > 0)
    rss_items = query.order_by(RSSItem.frontpage_id.asc(), RSSItem.pubDate.desc()).all()


    data = []
    now = datetime.now(montreal_tz)

    for item in rss_items:
        pubDate = pytz.utc.localize(item.pubDate).astimezone(montreal_tz)
        days_ago = (now.date() - pubDate.date()).days
        time_str = f"{pubDate.strftime('%H:%M')}"

        data.append({
            'source': item.source,
            'title': item.title,
            'description': item.description,
            'link': item.link,
            'pubDate': time_str,
            'uuid': item.uuid,
            'categorie': item.categorie
        })

    return render_template('unes.html',  rss_items=rss_items, data=data, selected_categories="unes", valid_categories=valid_categories)


@app.route('/a-propos', strict_slashes=False)
def about():
    return render_template('a-propos.html', valid_categories=valid_categories)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
