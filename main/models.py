from sqlalchemy import ForeignKey
from main import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#association table linking profile.id-to-order.id pairs
LinkOrder = db.Table('ProfileOrder', 
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'))
)

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

#customer profiles 
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)

    #"one" side of a one-to-many relationship (Profile-to-OrderQuantity) 
    quantities = db.relationship('OrderQuantity', back_populates= 'profile')
    #"left" side of a many-to-many relationship (Profile-to-Order) defined in an association table 
    orders = db.relationship('Order', back_populates='customers', secondary=LinkOrder, lazy='dynamic')
    
    def add_order(self, order, quantity):
        #adds item type if profile doesn't already own it
        if not self.owns_order(order):
            #adds profile-order id entry into association table 
            self.orders.append(order)
            #quantity of order for specific Profile is recoreded in OrderQuantity table
            order_quantity = OrderQuantity(order_name=order.name, quantity=quantity, profile=self)
            self.quantities.append(order_quantity)

    def modify_order(self, order, new_quantity):
        #modifies order if Profile has it
        if self.owns_order(order):
            #reads current quantity entry 
            entry = self.order_quantity(order)       
            #updates with new quantity 
            entry.quantity = new_quantity

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
    
    def order_quantity(self, order):
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

    def owner_profiles(self):
        #returns all Profiles that have ordered the item
        return Profile.query.join(
            LinkOrder, (LinkOrder.c.profile_id == Profile.id)
        ).filter(LinkOrder.c.order_id == self.id).order_by(Profile.username)

    def __repr__(self):
        return f'<{self.name}>'

#acts as a dictionary with name: quantity pairs
class OrderQuantity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_name = db.Column(db.String(64), index=True)
    quantity = db.Column(db.Integer, index=True)

    #profile_id set by OrderQuantity's Profile in their one-to-many relationship 
    profile_id = db.Column(db.Integer, ForeignKey('profile.id'))
    profile = db.relationship('Profile', back_populates='quantities')

@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))