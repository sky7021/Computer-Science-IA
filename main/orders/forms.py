from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields import StringField, SubmitField
from main.models import Order
import re

money = re.compile('|'.join([
    r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
    r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
    r'^\$(\d+\.?)$',         # e.g., $5.
    ]))

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

        if not re.compile(money).search(price.data):
            raise ValidationError('Enter cost in CAD')

#search for and edit fumo entries
#TODO: retrieve id attributes as a list
class SearchOrderForm(FlaskForm):
    submit = SubmitField('Search For Order')

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
        
        if self.original_name == self.changed_name and str(self.original_price) == cost.data:
            raise ValidationError('At least one parameter must be changed')

        if not re.compile(money).search(cost.data):
            raise ValidationError('Enter cost in CAD')

class EmptyForm(FlaskForm):
    submit = SubmitField()