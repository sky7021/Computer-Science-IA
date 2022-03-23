from sqlalchemy import ForeignKey, func
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

#association table linking profile.id-to-order.id pairs
#"child" table since it contains foreign keys
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
    orders = db.relationship('Order', back_populates='customers', secondary=LinkOrder, lazy='dynamic')
    profile_assoc = db.relationship('LinkOrder', back_populates='profile')
    
    def add_order(self, order, quantity, date):
        profile_order = LinkOrder(self.id, order.id, quantity, date)
        #adds item type if profile doesn't already own it
        if not self.owns_order(profile_order):
            #adds profile-order id entry into association table 
            self.orders.append(order)

    def modify_quantity(self, order, new_quantity, date):
        #modifies order if Profile has it
        if self.owns_order(order, date):
            #fetches current entry for profile-order pair on the specified date 
            entry = self.find_entry(order, date)       
            #updates with new quantity 
            entry.quantity = new_quantity

#TODO: modify owns_order and order_quantity methods 


    def remove_order(self, order):
        #removes order if Profile has it
        if self.owns_order(order):
            #removes entry from association table
            self.orders.remove(order)
            #removes the order's quantity object from the Profile's quantities table
            self.quantities.remove(self.order_quantity(order)) 
    
    def owns_order(self, order):
        #searches for entry in association table with Profile and order ids
        query = self.orders.filter(LinkOrder.c.order_id == order.id).count()
        if query > 0:
            return True
    
    def owned_orders(self):
        #returns list of orders
        return Order.query.join(
            LinkOrder, (LinkOrder.c.order_id == Order.id)).filter(LinkOrder.c.profile_id == self.id).order_by(Order.price)
    
    def find_entry(self, order):
        #returns quantity of order
        return OrderQuantity.query.join(
            Profile, (OrderQuantity.profile == self)
        ).filter(OrderQuantity.order_name == order.name).first()

    def __repr__(self):
        return f'<{self.username}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    price = db.Column(db.Integer, index=True)

    #"right" side of a many-to-many relationship (Profile-to-Order) defined in an association table 
    customers = db.relationship('Profile', back_populates='orders', secondary=LinkOrder, lazy='dynamic')
    order_assoc = db.relationship('LinkOrder', back_populates = 'order')

    def owner_profiles(self):
        #returns all Profiles that have ordered the item
        return Profile.query.join(
            LinkOrder, (LinkOrder.c.profile_id == Profile.id)
        ).filter(LinkOrder.c.order_id == self.id).order_by(Profile.username)
    
    def total_orders(self):
        #total number of orders for that item. 
        return OrderQuantity.query.with_entities(func.sum(OrderQuantity.quantity).label('mySum')).filter_by\
        (order_name = self.name).first().mySum
        
    def __repr__(self):
        return f'<{self.name}>'

#acts as a dictionary with name: quantity pairs
@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))