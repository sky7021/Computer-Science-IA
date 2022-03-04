from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField, BooleanField, SelectField, FloatField
from main.models import Profile, Order, Admin
import re

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

#creates customer profile
class CreateProfile(FlaskForm):
    username = StringField('Enter a name', validators=[DataRequired()])
    email = StringField('Enter an email', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

    def validate_email(self, email):
        mail = re.compile(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')

        if not re.compile(mail).search(email.data):
            raise ValidationError('Enter enter an email in a valid format')
        
        if Profile.filter_by(email=email.data).first() != None:
            raise ValidationError('That email has already been taken')

class MakeOrderForm(FlaskForm):
    name = StringField('Enter order name', validators=[DataRequired()])
    price = StringField('Enter order price', validators=[DataRequired()])
    submit = SubmitField('Add order')

    def validate_name(self, name):
        order  = Order.query.with_entities(Order.name).\
        filter(Order.name.ilike(f"%{name.data}%")).first()

        if order != None:
            raise ValidationError('That order has already been added')
    
    def validate_price(self, price):
        money = re.compile('|'.join([
        r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
        r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
        r'^\$(\d+\.?)$',         # e.g., $5.
        ]))

        if not re.compile(money).search(price.data):
            raise ValidationError('Enter cost in CAD')

#delete user account
class DeleteForm(FlaskForm):
    delete = BooleanField('Delete account (This action cannot be undone!)', validators=[DataRequired()])
    submit = SubmitField('Delete account')

#search for and edit fumo entries
#TODO: retrieve id attributes as a list
class SearchOrderForm(FlaskForm):
    submit = SubmitField('Search For Order')

class SearchProfileForm(FlaskForm):
    submit = SubmitField('Search For Profile')

#edit searched fumos
class EditOrderForm(FlaskForm):
    
    newname = StringField('Order Name', validators=[DataRequired()])
    #custom filter for cost? only to 2 decimal places
    cost = StringField('Cost (CAD)', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def __init__(self, order, *args, **kwargs):

        #__init__ for EditFumo now has all the methods of FlaskForm
        super(EditOrderForm, self).__init__(*args, **kwargs)
        self.original_name = order.name
        self.original_price = order.price
        self.changed_name = ''

    def validate_newname(self, newname):
        order = Order.query.filter_by(name=newname.data).first()

        #newname can be old one if price is different 
        if order != None and newname.data != self.original_name:
            raise ValidationError('Enter a different item name')
        self.changed_name = newname.data

    def validate_cost(self, cost):
        money = re.compile('|'.join([
        r'^\$?(\d*\.\d{1,2})$',  
        r'^\$?(\d+)$',           
        r'^\$(\d+\.?)$',         
        ]))
        
        if self.original_name == self.changed_name and str(self.original_price) == cost.data:
            raise ValidationError('At least one parameter must be changed')

        if not re.compile(money).search(cost.data):
            raise ValidationError('Enter cost in CAD')

class OrderProfileForm(FlaskForm):
    add_order = SelectField('Add / Modify items')
    remove_order = SelectField('Remove item from profile')
    submit = SubmitField('Save Changes')

    def __init__(self, profile, *args, **kwargs):

        #__init__ for Editorder now has all the methods of FlaskForm
        super(OrderProfileForm, self).__init__(*args, **kwargs)
        self.profile = profile
        self.addedorder = ''

    def validate_add_order(self, add_order):
        if add_order.data != 'Leave Blank':
            order = Order.query.filter_by(name=add_order.data).first()
            if self.profile.owns_order(order):
                raise ValidationError('Item already added')
        self.addedorder = add_order.data
    
    def validate_remove_order(self, remove_order):
        #no need to check for removing a nonexistant order; already checked in given options
        print(self.addedorder)
        if self.addedorder == 'Leave Blank' and remove_order.data == 'Leave Blank':
            raise ValidationError('No changes have been made')
                    
class EmptyForm(FlaskForm):
    submit = SubmitField()
        