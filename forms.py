from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired,  Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SubmitRecentGamesForm(FlaskForm):
    """Form for submitting recent games"""
    username = StringField('Username', validators=[DataRequired()])
    tag = StringField('Tag', validators=[DataRequired()])
    region  = SelectField('Region', choices=[('americas', 'Americas'), ('asia', 'Asia'), ('europe', 'EMEA')])
