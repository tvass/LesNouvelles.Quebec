import os
import time
import secrets
import html
import feedparser
import yaml

from datetime import datetime, timedelta
from html.parser import HTMLParser
from sqlalchemy import create_engine, insert, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration et initialisation de la base de données
Base = declarative_base()
db_path = os.path.join(os.getcwd(), '/db/news.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
if not os.path.exists(db_path):
    open(db_path, 'w').close()

DATABASE_URL = f'sqlite:///{db_path}'

class RSSItem(Base):
    __tablename__ = 'rss_items'
    link = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pubDate = Column(DateTime, nullable=True)
    uuid = Column(Text(24), nullable=False)
    source = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    frontpage_id = Column(Integer, nullable=False, default=0)

engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Fonctions utilitaires
def is_link_in_db(link):
    """Vérifie si le lien est déjà en base."""
    with Session() as session:
        return session.query(RSSItem.link).filter_by(link=link).first() is not None

def strip_html_tags(text):
    """Supprime les balises HTML du texte."""
    parser = MLStripper()
    parser.feed(text)
    return parser.get_data()

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

def insert_rss_feed(url, source_title, category):
    """Insère un flux RSS dans la base de données."""
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        pubDate = datetime(*entry.published_parsed[:6]) if "published_parsed" in entry else datetime.utcnow()

        if is_link_in_db(link):
            print(f"⏩ Ignoré (déjà en base) : {title}")
            continue

        # Ignorer les articles de plus de 48 heures
        if pubDate < datetime.utcnow() - timedelta(hours=48):
            print(f"⏩ Ignoré (plus vieux que 48h) : {title}")
            continue

        description = entry.get("description", "").strip()

        with Session() as session:
            stmt = insert(RSSItem).values(
                title=html.unescape(strip_html_tags(title)),
                link=link,
                description=html.unescape(strip_html_tags(description)),
                pubDate=pubDate,
                uuid=secrets.token_hex(12),
                source=source_title,
                categorie=category
            ).prefix_with("OR IGNORE")  # SQLite ignore les doublons
            session.execute(stmt)
            session.commit()

        print(f"✅ Ajouté : {title}")
        time.sleep(2)

def set_frontpage(frontpage_url, source_title):
    """Met à jour les articles en les plaçant en frontpage selon leur position."""
    feed = feedparser.parse(frontpage_url)
    with Session() as session:
        # Réinitialiser les frontpage_id pour cette source
        session.query(RSSItem).filter_by(source=source_title).update({"frontpage_id": 0})
        session.commit()

        for position, entry in enumerate(feed.entries, start=1):
            link = entry.get("link", "").strip()
            article = session.query(RSSItem).filter_by(link=link).first()

            if article:
                article.frontpage_id = position
                print(f"🔄 Mise à jour : {article.title} (frontpage_id = {position})")

        session.commit()

def clean_old_entries(max_entries=1000):
    """Nettoie les anciens articles en gardant un nombre maximum d'entrées."""
    with Session() as session:
        total_entries = session.query(RSSItem).count()
        if total_entries > max_entries:
            entries_to_delete = session.query(RSSItem).order_by(RSSItem.pubDate).limit(total_entries - max_entries).all()
            for entry in entries_to_delete:
                session.delete(entry)
            session.commit()
            print(f"🧹 Nettoyage effectué : {len(entries_to_delete)} articles supprimés.")

with open('source.yaml', 'r', encoding='utf-8') as file:
    sources_data = yaml.safe_load(file)

while True:
    for source in sources_data["sources"]:
        clean_old_entries(max_entries=1000)
        print("Processing source:", source)
        for key, details in source.items():
            print(f"Checking key: {key}")
            if "rss" in details:
                for rss in details["rss"]:
                    rss_url = rss["url"]
                    category = rss["category"]
                    print(f"RSS URL: {rss_url} | Category: {category}")
                    insert_rss_feed(rss_url, details["title"], category)
            else:
                print(f"No RSS found for {details['title']}")

            if "frontpage" in details:
                for frontpage_rss in details["frontpage"]:
                    print(f"Frontpage RSS URL: {frontpage_rss} | Source: {details['title']}")
                    set_frontpage(frontpage_rss, details["title"])

    time.sleep(300)
