from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    # create password entry box
    name = StringField(label='What ur name?', name="name", id="", validators=[DataRequired(), Length(2, 16)])
    # create submit button
    submit = SubmitField("Login")