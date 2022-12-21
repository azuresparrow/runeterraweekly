from flask import Flask, request, render_template, redirect, flash, session, jsonify
from models import db, connect_db, User, Challenge, Match, Card, Requirement
from sqlalchemy import func as alchemyFn
from forms import SubmitRecentGamesForm
from secret import sessionkey

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///runeterraweekly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = sessionkey
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
with app.app_context():
    db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""
    return render_template('404.html'), 404


@app.route('/')
def current_challenge():
    """The home route, presents the currently ongoing deck-challenge it's possible to submit games for"""
    challenge = Challenge.get_active_challenge()
    requirements = challenge.fetch_requirements()
    user = None
    if session.get('uid'):
        user = User.query.get_or_404(session['uid'])
    submit_form = SubmitRecentGamesForm(obj=user)
    return render_template("home.html", challenge=challenge, requirements=requirements, form=submit_form, user=user)


@app.route('/user/<uid>/challenge/<cid>')
def user_history(uid, cid):
    """User-oriented view of past challenges preserving their match-history"""
    challenge = Challenge.query.get_or_404(cid)
    # if the challenge path is the currently ongoing one, direct the user to the homepage instead.

    user = User.query.get_or_404(uid)
    matches = Match.query.filter(Match.challenge_id == cid, Match.riot_id == user.riot_id, Match.valid, Match.game_mode == 'Constructed', Match.game_type != 'AI')
    for match in matches:
        match.deck_code
    return render_template("user.html", matches=matches, challenge=challenge, user=user)

@app.route('/user/<cid>', methods=["POST"])
def search_results(cid):
    """Search for user info to direct them to the correct challenge page"""
    form= SubmitRecentGamesForm()
    if form.validate_on_submit():
        server = form.region.data
        username = form.username.data
        tagline = form.tag.data
        user = User.fetch_user(username=username, tag=tagline, region=server)
        return redirect("/user/{}/challenge/{}".format(user.id, cid))
    else:
        return redirect("/challenge/{}".format(cid))

@app.route('/cards')
def cards():
    """Simple card list, mostly for admin purposes"""
    cards = Card.query.order_by("card_name").all()
    return render_template("cards.html", cards = cards)


@app.route('/cards/<rarity>')
def cards_at_rarity(rarity):
    """Cards of a rarity"""
    cards = Card.query.filter(alchemyFn.lower(Card.card_rarity) == rarity)
    return render_template("cards.html", cards = cards)

@app.route('/card/<code>')
def get_card(code):
    """Card with a specific card code"""
    card = Card.query.get_or_404(code)
    return render_template("card.html", card = card)

@app.route('/challenges/<id>')
def challenge(id):
    """Detail view of a past challenge"""
    if session['uid']:
        return redirect("/user/{}/challenge/{}".format(session['uid'], id))
    challenge = Challenge.query.get_or_404(id)
    submit_form = SubmitRecentGamesForm()
    user = None
    return render_template("challenge.html", challenge=challenge, form=submit_form, user=user)

@app.route('/end_session/')
def end_session():
    session['uid'] = ''
    return redirect('/')

@app.route('/challenges/')
def challenge_list():
    """Grid of past challenges"""
    current = Challenge.get_active_challenge()
    challenges = Challenge.query.join(Requirement).filter(Challenge.id != current.id)
    user = None
    if session['uid']:
        user = User.query.get_or_404(session['uid'])
    return render_template("challenges.html", challenges=challenges, user=user)
"""
@app.route('/leaderboard/')
def leaderboard_list():
    current = Challenge.get_active_challenge()
    response = Match.query.join(User, Match.riot_id == User.riot_id).filter(Match.challenge_id == current.id, Match.valid)
    print(response[0].user.username)
    response = Match.top_5_quantity(current.id)
    response =  Match.query.filter(Match.challenge_id == current.id, Match.riot_id == 'Bo5EyjrYYk440RStfc6uiuDv_uHmmS7f506WjB_OnKwv88ih5L_7AgFBVNFKigkOzp85_xS3SiVu8g', Match.valid == True, Match.game_result == "win" ).count()
    print(response)
    response2 =  Match.query.filter(Match.challenge_id == current.id, Match.riot_id == 'Bo5EyjrYYk440RStfc6uiuDv_uHmmS7f506WjB_OnKwv88ih5L_7AgFBVNFKigkOzp85_xS3SiVu8g', Match.valid == True, Match.game_result == "win" )
    print(response2)
    return render_template("leaderboard.html",challenge =current, cumulative=response)
    #.filter(Match.challenge_id == current.id, Match.valid)"""

@app.route('/submit/', methods=["POST"])
def submit_games():
    """Handle submission of new data for the current deckbuilding challenge"""
    form= SubmitRecentGamesForm()
    if form.validate_on_submit():
        server = form.region.data
        username = form.username.data
        tagline = form.tag.data

        # get user by username/tagline/region
        try:
            user = User.fetch_user(username=username, tag=tagline, region=server)
            session['uid'] = user.id
        except KeyError:
            flash("No {} found with that tag/region".format(username), 'danger')
            return redirect('/')
        matchList = []
        # pull that user's match ids
        matchIDs = user.fetch_recent_matchIDs()
        
        for match_id in matchIDs:
            # check if match is already recorded internally to save external API calls
            try:
                match = Match.fetch_match(match_id, server=user.region, puuid=user.riot_id)
                if match:
                    matchList.append(match)
            except:
                flash("Error while processing match data", 'danger')
                return redirect('/')
        flash("{} new game{} added".format(len(matchList), '' if len(matchList) == 1 else 's'),'info')
        return redirect("/user/{}/challenge/{}".format(user.id, Challenge.get_active_challenge().id))
    else:
        return redirect("/")
