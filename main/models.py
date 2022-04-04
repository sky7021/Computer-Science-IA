from sqlalchemy import ForeignKey, func, and_
from main import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#client logs in through admin to access site 
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    #hashed password value stored for security
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        #converts string to hash 
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        #checks against stored hash
        return check_password_hash(self.password_hash, password)

class LinkOrder(db.Model):
    #directly accepts Profile object in intantiation to avoid dealing with ids
    #Profile objects now have the 'profiles_assoc' method to view the LinkOrder object
    #representing their row in this table
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), primary_key = True)
    profile = db.relationship('Profile', back_populates='profile_assoc')

    #same as above but for orders
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key = True)
    order = db.relationship('Order', back_populates='order_assoc')

    quantity = db.Column(db.Integer, index=True)
    order_date = db.Column(db.Date, index=True)

#customer profiles 
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)

    #table with profile, orders, their quantities, and the date
    profile_assoc = db.relationship('LinkOrder', back_populates='profile', cascade='all, delete-orphan')
    
    #keyword arguements
    def add_order(self, order, quantity, date):

        #adds item type if profile doesn't already own it
        if not self.owns_order(order, date):

            profile_order = LinkOrder(profile=self, order=order, quantity=quantity, order_date=date)
            #adds profile-order id entry into association table based on relationship
            self.profile_assoc.append(profile_order)

    def modify_quantity(self, order, new_quantity, date):
        #modifies order if Profile has it
        if self.owns_order(order, date):
            #fetches entry on specified date
            entry = self.get_order(order, date)       
            #updates with new quantity 
            entry.quantity = new_quantity

#TODO: modify owns_order and order_quantity methods 

    def remove_order(self, order, date):
        #removes order if Profile has it
        if self.owns_order(order, date):
            #removes entry from association table
            self.profile_assoc.remove(self.get_order(order, date))
    
    def owns_order(self, order, date):
        #searches for entry in association table with profile, order, and date
        if self.get_order(order, date) != None:
            return True
    
    def get_order(self, order, date):
        #profile, order, and date all match
        return LinkOrder.query.filter(LinkOrder.profile == self, LinkOrder.order == order, LinkOrder.order_date == date).first()

    #returns list of orders on a given date
    def owned_orders(self, date):
        #orders that have been ordered at least once have their profile / dates compared with the ones given
        return Order.query.join(
            LinkOrder, (LinkOrder.order_id == Order.id)).filter(
                LinkOrder.profile == self, LinkOrder.order_date == date
                ).order_by(Order.price).all()
    
    def __repr__(self):
        return f'<{self.username}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    price = db.Column(db.Integer, index=True)

    #"right" side of a many-to-many relationship (Profile-to-Order) defined in an association table 
    #customers = db.relationship('Profile', back_populates='orders', secondary=LinkOrder, lazy='dynamic')
    order_assoc = db.relationship('LinkOrder', back_populates = 'order', cascade='all, delete-orphan')

    def owner_profiles(self, date):
        #keeps profiles with an entry in the table

        return Profile.query.join(
            LinkOrder, (LinkOrder.profile_id == Profile.id)
        ).filter(LinkOrder.order == self, LinkOrder.order_date == date).order_by(Profile.username).all()
    
    #returns all orders on a given date
    def total_orders(self, date):

        #select the above, add up values in the quantity column for those 
        return LinkOrder.query.with_entities(func.sum(LinkOrder.quantity).label('mySum')).filter_by(
            order = self, order_date = date
        ).first().mySum
        
    def __repr__(self):
        return f'<{self.name}>'

#acts as a dictionary with name: quantity pairs
@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))