from main import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

LinkOrder = db.Table('ProfileOrder', 
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'))
)

#user login class 
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
#Profile inherits methods of UserMixin and db.Model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)

    orders = db.relationship('Order', back_populates='customers', secondary=LinkOrder, lazy='dynamic'
    )
    
    def add_order(self, order):
        #adds item type if profile doesn't already own it
        if not self.owns_order(order):
            self.orders.append(order)
    
    def remove_order(self, order):
        #removes item if Profile has it
        if self.owns_order(order):
            self.orders.remove(order)
    
    def owns_order(self, order):
        query = self.orders.filter(LinkOrder.c.order_id == order.id).count()
        if query > 0:
            return True
    
    def owned_orders(self):
        #filter for orders of profile
        return Order.query.join(
            LinkOrder, (LinkOrder.c.order_id == Order.id)).filter(LinkOrder.c.profile_id == self.id).order_by(Order.price)

    def __repr__(self):
        return f'<{self.username}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    price = db.Column(db.Integer, index=True)

    customers = db.relationship('Profile', back_populates='orders', secondary=LinkOrder, lazy='dynamic')

    def owner_profiles(self):
        return Profile.query.join(
            LinkOrder, (LinkOrder.c.profile_id == Profile.id)).filter(LinkOrder.c.order_id == self.id).order_by(Profile.username)

    def __repr__(self):
        return f'<{self.name}>'

@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))