from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from main.models import Admin

#login page
class LoginForm(FlaskForm):
    username = StringField('Enter your username', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired()])
    submit = SubmitField('Submit')

#create user account
class CreateForm(FlaskForm):
    username = StringField('Enter a username', validators=[DataRequired()])
    password = PasswordField('Enter a password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm your password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create account')

    #custom validator, checks if username is already taken

    def validate_username(self, username):
        if Admin.query.filter_by(username=username.data).first() != None:
            raise ValidationError('That username is already taken')

class DeleteForm(FlaskForm):
    delete = BooleanField('Delete account (This action cannot be undone!)', validators=[DataRequired()])
    submit = SubmitField('Delete account')
