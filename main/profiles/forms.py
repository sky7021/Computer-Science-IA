from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from main.models import Profile, Order
import re

#creates customer profile
class CreateProfile(FlaskForm):
    username = StringField('Enter a name', validators=[DataRequired()])
    email = StringField('Enter an email', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

    def validate_email(self, email):
        mail = re.compile(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')

        if not re.compile(mail).search(email.data):
            raise ValidationError('Enter enter an email in a valid format')
        
        if Profile.query.filter_by(email=email.data).first() != None:
            raise ValidationError('That email has already been taken')

class SearchProfileForm(FlaskForm):
    submit = SubmitField('Search For Profile')

class OrderProfileForm(FlaskForm):
    add_order = SelectField('Add / Modify items')
    add_quantity = StringField('Number of ordered item')
    remove_order = SelectField('Remove item from profile')
    submit = SubmitField('Save Changes')

    def __init__(self, profile, *args, **kwargs):

        #__init__ for Editorder now has all the methods of FlaskForm
        super(OrderProfileForm, self).__init__(*args, **kwargs)
        self.profile = profile
        self.addedorder = ''

    def validate_add_order(self, add_order):
        self.addedorder = add_order.data
    
    def validate_add_quantity(self, add_quantity): 
        #implement regex for checking integers
        
        if self.addedorder != 'Leave Blank' and add_quantity.data != '':
            if int(add_quantity.data) <= 0:
                raise ValidationError('Quantity cannot be 0 or less')

            order = Order.query.filter_by(name=self.addedorder).first()
            #already added item with same quantity
            if self.profile.owns_order(order) and self.profile.order_quantity(order).quantity == int(add_quantity.data):
                raise ValidationError('Item already added')
                
        if self.addedorder != 'Leave Blank' and add_quantity.data == '':
            raise ValidationError('Quantity of order cannot be blank')
        if self.addedorder == 'Leave Blank' and add_quantity.data != '':
            raise ValidationError('Order cannot be blank')
    
    def validate_remove_order(self, remove_order):
        #no need to check for removing a nonexistant order; already checked in given options
        if self.addedorder == 'Leave Blank' and remove_order.data == 'Leave Blank':
            raise ValidationError('No changes have been made')

class EmptyForm(FlaskForm):
    submit = SubmitField()
