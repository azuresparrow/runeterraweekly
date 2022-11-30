from flask import Flask, request, render_template, redirect, flash, session, jsonify
from models import db, connect_db, User, Challenge, Match, Requirement, Deck, DeckCard, Card, DeckFaction
from secret import riotkey
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///runeterraweekly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "supersecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
with app.app_context():
    db.create_all()


@app.route('/')
def default_route():
    return render_template("home.html")

@app.route('/cards')
def cards():
    return render_template("cards.html")


"""Populate data with a particular set id"""    
"""
@app.route('/load/<set>')
def load_card_data(set):
    
    with open('static/data/set{}-en_us.json'.format(set), 'r') as f:
        text = f.read()
        cards = json.loads(text)
        cardList = []
        for card in cards:
            if card["collectible"]:
                cardObj = Card(card_code=card["cardCode"], card_name=card["name"], card_rarity=card["rarity"])
                db.session.add(cardObj)
                db.session.commit()
        print(cardList)
        return render_template("home.html", set=set)
"""