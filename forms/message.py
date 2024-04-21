from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class RegisterMessage(FlaskForm):
    text = StringField("Сообщение", validators=[DataRequired()])
    submit = SubmitField('Отправить')

