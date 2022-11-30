from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Establishes the connection"""
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """Users can log in, and link to their riot account to submit challenge stats"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                   primary_key=True, 
                   autoincrement=True)
    username = db.Column(db.String(30), 
                    unique=True,
                    nullable=False)
    passwordhash = db.Column(db.String(80), 
                    nullable=False)
    isAdmin = db.Column(db.Boolean, 
                    default=False)


    game_name = db.Column(db.String(30),
                    nullable=False)
    tag = db.Column(db.String(8),
                    nullable=False)
    riot_id = db.Column(db.String(50),
                    nullable=False)

    matches = db.relationship('Match', back_populates='user', cascade="all, delete", passive_deletes=True)

    

class Match(db.Model):
    """Matches represent a recorded game, this is the most expensive API call so whether the data was useful or not it should be stored to avoid repeat calls"""
    __tablename__ = 'matches'
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    riot_id = db.Column(db.String(50), nullable=False)
    opponent_id  = db.Column(db.String(50))
    deck_code = db.Column(db.String(50))
    game_start = db.Column(db.DateTime, 
                    nullable=False)
    user_id = db.Column(db.Integer,
                    db.ForeignKey('users.id', ondelete='CASCADE'))

    game_type = db.Column(db.String(10))

    user = db.relationship('User', back_populates='matches')

class Challenge(db.Model):
    """A weekly deckbuilding challenge, """
    __tablename__ = 'challenges'
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    challenge_start = db.Column(db.DateTime, 
                    nullable=False)
    challenge_end = db.Column(db.DateTime, 
                    nullable=False)
    name = db.Column(db.Text, nullable = False, unique = True)

class Requirement(db.Model):
    """the cards and quantities required to meet the challenge"""
    __tablename__ = 'requirements'
    card_code = db.Column(db.String(15),primary_key=True)
    card_quantity = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), primary_key=True)

class Card(db.Model):
    """Some basic info about a card"""
    __tablename__ = 'cards'
    card_code = db.Column(db.String(15),primary_key=True)
    card_name = db.Column(db.String(50))
    card_rarity = db.Column(db.String(10))

class DeckCard(db.Model):
    """how many of a card a deck has"""
    __tablename__ = 'deckcards'
    card_code = db.Column(db.String(15),primary_key=True)
    deck_code = db.Column(db.String(50),primary_key=True)
    card_quantity = db.Column(db.Integer)

class Deck(db.Model):
    """List of decks"""
    __tablename__ = 'decks'
    deck_code = db.Column(db.String(50),primary_key=True)

class DeckFaction(db.Model):
    """Factions tied to a deck"""
    __tablename__ = 'deckfactions'
    deck_code = db.Column(db.String(50),primary_key=True)
    faction = db.Column(db.String(50), primary_key=True)


