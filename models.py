from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
from secret import riotkey
from lor_deckcodes import LoRDeck, CardCodeAndCount
from sqlalchemy import func as alchemyFn
import json

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

    riot_id = db.Column(db.String(100), unique=True,
                nullable=False)

    username = db.Column(db.String(30), 
                    nullable=False)

    tag = db.Column(db.String(8),
                    nullable=False)

    region = db.Column(db.String(10), nullable=False)

    @classmethod
    def fetch_user(cls, username, tag, region):
        user = cls.query.filter_by(username=username, tag=tag, region=region).first()
        if not user:
            uuid_apiCall = "https://{server}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tagline}?api_key={key}".format(server=region, username=username, tagline=tag, key=riotkey)
            uuid_response = requests.get(uuid_apiCall)
            
            uuid = uuid_response.json()['puuid']
            user = User(riot_id= uuid, region=region, username=username, tag=tag)
            db.session.add(user)
            db.session.commit()
        return user

    def fetch_recent_matchIDs(cls):
        matches_apiCall = "https://{server}.api.riotgames.com/lor/match/v1/matches/by-puuid/{puuid}/ids?api_key={key}".format(server=cls.region, puuid=cls.riot_id, key=riotkey)
        matches_response = requests.get(matches_apiCall)
        return matches_response.json()
    """
    passwordhash = db.Column(db.String(80), 
                    nullable=False)
    isAdmin = db.Column(db.Boolean, 
                    default=False)
    """

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
    requirements = db.relationship('Requirement', backref='challenge')

    def validate_deck(cls, deck_code):
        requirements = Requirement.query.filter(Requirement.challenge_id == cls.id)
        for requirement in requirements:
            if not requirement.test(deck_code):
                return False
        return True

    @classmethod
    def get_active_challenge(cls):
        active = Challenge.query.order_by(Challenge.challenge_end.desc()).first()
        return active

    def fetch_requirements(cls):
        return Requirement.query.filter(Requirement.challenge_id == cls.id)

class Match(db.Model):
    """Matches represent a recorded game, this is the most expensive API call so whether the data was useful or not it should be stored to avoid repeat calls"""
    __tablename__ = 'matches'
    id = db.Column(db.String(100),
                   primary_key=True)
    riot_id = db.Column(db.String(100), db.ForeignKey(User.riot_id), nullable=False)
    
    deck_code = db.Column(db.String(150))
    player_factions = db.Column(db.String(300))
    player_champions = db.Column(db.String(300))

    game_mode = db.Column(db.String(30))
    game_result = db.Column(db.String(10))
    game_start = db.Column(db.DateTime, 
                    nullable=False)
    game_type = db.Column(db.String(30))

    opponent_id  = db.Column(db.String(100))
    opponent_deck = db.Column(db.String(150))
    opponent_factions = db.Column(db.String(300))
    opponent_champions = db.Column(db.String(300))

    challenge_id = db.Column(db.Integer,  db.ForeignKey(Challenge.id))
    valid = db.Column(db.Boolean)
    user = db.relationship('User', backref='matches')

    @classmethod
    def match_stats_for_challenge(cls, uuid, chal_id):
        wins = cls.query.filter(cls.challenge_id == chal_id, cls.riot_id == uuid, cls.valid, cls.game_result == "win" ).count()
        losses = cls.query.filter(cls.challenge_id == chal_id, cls.riot_id == uuid, cls.valid, cls.game_result == "loss" ).count()
        results = {
            wins: wins,
            losses:losses
        }
        return results


    @classmethod
    def fetch_match(cls, match_id, server, puuid):
        match = cls.query.get(match_id)
        if not match:
            match_apiCall = "https://{server}.api.riotgames.com/lor/match/v1/matches/{matchId}?api_key={key}".format(server=server, matchId=match_id, key=riotkey)
            match_response = requests.get(match_apiCall)
            data = match_response.json()

            challenge = Challenge.get_active_challenge()

            playerNumb =  1 if data['info']['players'][0]['puuid'] != puuid else 0
            deckCode = data['info']['players'][playerNumb]['deck_code']
            
            championcsv = Deck.get_champions(deckCode)
            Deck.add_if_not_found(deckCode, puuid)
            factionList = data['info']['players'][playerNumb]['factions']
            factions = []
            for faction in factionList:
                factions.append(faction.lstrip("faction_").rstrip("_Name"))
            playerFactioncsv = ','.join(factions)
            matchInfo = {
                'id': match_id,
                'challenge_id': challenge.id,
                'riot_id': puuid,
                'game_mode': data['info']['game_mode'],
                'deck_code' : deckCode,
                'player_factions':playerFactioncsv,
                'player_champions':championcsv,
                'valid' : challenge.validate_deck(deckCode),
                'game_type': data['info']['game_type'],
                'game_result' : data['info']['players'][playerNumb]['game_outcome'],
                'game_start' : data['info']["game_start_time_utc"],
            }
            if data['info']['game_mode'] != 'ThePathOfChampions':
                matchInfo['opponent_deck'] = data['info']['players'][(playerNumb + 1) % 2]['deck_code']
                matchInfo['opponent_id'] = data['info']['players'][(playerNumb + 1) % 2]['puuid']
                factionList = data['info']['players'][(playerNumb + 1) % 2]['factions']
                factions = []
                for faction in factionList:
                    factions.append(faction.lstrip("faction_").rstrip("_Name"))
                opponentFactioncsv = ','.join(factions)
                matchInfo['opponent_factions'] = opponentFactioncsv
                matchInfo['opponent_champions'] = Deck.get_champions(matchInfo['opponent_deck'])
                Deck.add_if_not_found(matchInfo['opponent_deck'], matchInfo['opponent_id'])
            match = Match(**matchInfo)
            db.session.add(match)
            db.session.commit()
            #for reporting newly added valid matches
            if matchInfo['valid']:
                return match

class Requirement(db.Model):
    """the cards and quantities required to meet the challenge"""
    __tablename__ = 'requirements'
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    card_code = db.Column(db.String(15))
    card_quantity = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id))

    def test(cls, deck_code):
        if deck_code:
            deck = LoRDeck.from_deckcode(deck_code)
            for card in deck.cards:
                if card.card_code == cls.card_code and card.count >= cls.card_quantity:
                    return True
        return False

 

class Card(db.Model):
    """Some basic info about a card"""
    __tablename__ = 'cards'
    card_code = db.Column(db.String(15),primary_key=True)
    card_name = db.Column(db.String(50))
    card_rarity = db.Column(db.String(10))

    @classmethod
    def reload_card_db(cls):
        sets = ['1', '2', '3', '4', '5', '6', '6cde']
        for set in sets:
            with open('static/data/set{}-en_us.json'.format(set), 'r') as f:
                text = f.read()
                cards = json.loads(text)
                for card in cards:
                    if card["collectible"]:
                        cardObj = Card(card_code=card["cardCode"], card_name=card["name"], card_rarity=card["rarity"])
                        db.session.add(cardObj)
                        db.session.commit()

class Deck(db.Model):
    """List of decks"""
    __tablename__ = 'decks'
    deck_code = db.Column(db.String(150),primary_key=True)
    first = db.Column(db.String(100))

    @classmethod
    def add_if_not_found(cls, deck_code, uuid):
        found = cls.query.get(deck_code)
        if not found:
            deck = Deck(deck_code=deck_code, first = uuid)
            db.session.add(deck)
            db.session.commit()
    @classmethod
    def get_champions(cls, deck_code):
        result = []
        if deck_code:
            deck = LoRDeck.from_deckcode(deck_code)
            for card in deck.cards:
                obj = Card.query.filter(Card.card_code == card.card_code).first() 
                if obj.card_rarity == 'Champion':
                    result.append(obj.card_code)
        return ','.join(result)

