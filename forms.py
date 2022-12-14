from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class SubmitRecentGamesForm(FlaskForm):
    """Form for submitting recent games"""
    username = StringField('Username', validators=[DataRequired()])
    tag = StringField('Tag', validators=[DataRequired()])
    region  = SelectField('Region', choices=[('americas', 'Americas'), ('asia', 'Asia'), ('europe', 'EMEA')])
