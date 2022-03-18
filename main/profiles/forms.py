from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired
from main.models import Profile, Order
import re

#Form class is a subclass of FlaskForm
class CreateProfile(FlaskForm):
    #class variables as fields
    username = StringField('Enter a name', validators=[DataRequired()])
    email = StringField('Enter an email', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

    #'validate_<class variable>' notation checks that field's input upon form submission
    def validate_email(self, email):
        #regex for emails
        #source: https://www.geeksforgeeks.org/write-regular-expressions/
        mail = re.compile(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')

        #not in email format
        if not re.compile(mail).search(email.data):
            raise ValidationError('Enter enter an email in a valid format')
        
        if Profile.query.filter_by(email=email.data).first() != None:
            raise ValidationError('That email has already been taken')

class OrderProfileForm(FlaskForm):
    #form fields
    add_order = SelectField('Add / Modify items')
    add_quantity = StringField('Number of ordered item')
    remove_order = SelectField('Remove item from profile')
    submit = SubmitField('Save Changes')

    #variables can be passed into the form upon its initialization as an object
    def __init__(self, profile, *args, **kwargs):

        #__init__ for Editorder now has all the methods of FlaskForm
        super(OrderProfileForm, self).__init__(*args, **kwargs)
        self.profile = profile
        self.addedorder = ''

    def validate_add_order(self, add_order):
        #saves add_order for later validation
        self.addedorder = add_order.data
    
    def validate_add_quantity(self, add_quantity): 
        #add_order and add_quantity fields are filled
        if self.addedorder != 'Leave Blank' and add_quantity.data != '':
            try:
                if int(add_quantity.data) <= 0:
                    raise ValidationError('Quantity cannot be 0 or less')
            except:
                raise ValidationError('Quantity must be an integer')

            #queried Order object when first two fields are filled with acceptable data
            order = Order.query.filter_by(name=self.addedorder).first()
            #An entry for order with the same quantity already exists
            
            if self.profile.owns_order(order) and self.profile.order_quantity(order).quantity == int(add_quantity.data):
                raise ValidationError('Item already added')
      
        
        #additional exceptions
        #filled order and unfilled quantity
        if self.addedorder != 'Leave Blank' and add_quantity.data == '':
            raise ValidationError('Quantity of order cannot be blank')
        #filled quantity and unfilled order
        if self.addedorder == 'Leave Blank' and add_quantity.data != '':
            raise ValidationError('Order cannot be blank')
    
    #blank form is submitted
    def validate_remove_order(self, remove_order):
        if self.addedorder == 'Leave Blank' and remove_order.data == 'Leave Blank':
            raise ValidationError('No changes have been made')

class EmptyForm(FlaskForm):
    submit = SubmitField()
