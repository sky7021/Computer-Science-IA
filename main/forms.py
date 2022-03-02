from flask_wtf import FlaskForm
from sqlalchemy import String
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
            raise ValidationError('That usename is already taken')

#creates customer profile
class CreateProfile(FlaskForm):
    username = StringField('Enter a name', validators=[DataRequired()])
    email = StringField('Enter an email', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

    def validate_email(self, email):
        mail = re.compile(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')

        if not re.compile(mail).search(email.data):
            raise ValidationError('Enter enter an email in a valid format')

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

#delete fumo
class DeleteOrderForm(FlaskForm):
    delete = BooleanField('Delete Order (This action cannot be undone!)', validators=[DataRequired()])
    submit = SubmitField('Delete Order')

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

    def __init__(self, original_name, *args, **kwargs):

        #__init__ for EditFumo now has all the methods of FlaskForm
        super(EditOrderForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
        
    def validate_cost(self, cost):
        money = re.compile('|'.join([
        r'^\$?(\d*\.\d{1,2})$',  
        r'^\$?(\d+)$',           
        r'^\$(\d+\.?)$',         
        ]))

        if not re.compile(money).search(cost.data):
            raise ValidationError('Enter cost in CAD')

    def validate_newname(self, newname):
        if newname.data  is not self.original_name:
            order = Order.query.filter_by(name=newname.data).first()

            if order != None:
                raise ValidationError('Enter a different item name')

class OrderProfileForm(FlaskForm):
    add_order = SelectField('Add items to profile')
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
        #make sure its not equal to add_order
        if remove_order != self.addedorder:
            if remove_order.data != 'Leave Blank':
                order = Order.query.filter_by(name=remove_order.data).first()
                if not self.profile.owns_order(order):
                    raise ValidationError('Item not added, cannot remove')
        else:
            raise ValidationError('Cannot add and remove the same item')
        

        