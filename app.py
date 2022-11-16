from flask import Flask, request, render_template, redirect, flash, session

from secret import riotkey

app = Flask(__name__)

app.config['SECRET_KEY'] = "supersecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

RESPONSES_KEY = "responses"

@app.route('/')
def default_route():
    return render_template("home.html")
