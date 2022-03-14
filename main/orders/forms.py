from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields import StringField, SubmitField
from main.models import Order
import re

#regular expression for money
#source: https://stackoverflow.com/questions/2150205/can-somebody-explain-a-money-regex-that-just-checks-if-the-value-matches-some-pa
money = re.compile('|'.join([
    r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
    r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
    r'^\$(\d+\.?)$',         # e.g., $5.
    ]))

class MakeOrderForm(FlaskForm):
    #class variables as fields (label, validators)
    name = StringField('Enter order name', validators=[DataRequired()])
    price = StringField('Enter order price', validators=[DataRequired()])
    submit = SubmitField('Add order')

    #'validate_<class variable>' notation checks that field's input upon form submission
    def validate_name(self, name):
        #searches for entry with the same name regardless of capitalization
        order  = Order.query.with_entities(Order.name).\
        filter(Order.name.ilike(f"%{name.data}%")).first()

        if order != None:
            raise ValidationError('That order has already been added')
    
    def validate_price(self, price):
        #input not in money format
        if not re.compile(money).search(price.data):
            raise ValidationError('Enter cost in CAD')

class EditOrderForm(FlaskForm):
    newname = StringField('Order Name', validators=[DataRequired()])
    cost = StringField('Cost (CAD)', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def __init__(self, order, *args, **kwargs):

        #__init__ for EditOrderForm now has all the methods of FlaskForm
        super(EditOrderForm, self).__init__(*args, **kwargs)
        self.original_name = order.name
        self.original_price = order.price
        self.changed_name = ''

    def validate_newname(self, newname):
        order = Order.query.filter_by(name=newname.data).first()

        #tries to change name to an order already in the database that does not have
        #its original name since name can be the same if price changes
        if order != None and newname.data != self.original_name:
            raise ValidationError('Enter a different item name')
        self.changed_name = newname.data

    def validate_cost(self, cost):
        
        #submits unchanged form
        if self.original_name == self.changed_name and str(self.original_price) == cost.data:
            raise ValidationError('At least one parameter must be changed')

        if not re.compile(money).search(cost.data):
            raise ValidationError('Enter cost in CAD')

class EmptyForm(FlaskForm):
    submit = SubmitField()