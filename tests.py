import unittest
from main import create_app, db
from main.models import Profile, Order, OrderQuantity
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #testing new total cost calculator
    def test_order_ownership(self):
        p1 = Profile(username='sky7021', email='example1@testmail.com')
        p2 = Profile(username='baldspot', email='example2@testmail.com')
        db.session.add_all([p1, p2])

        f1 = Order(name='Cirno', price=50)
        f2 = Order(name='Tenshi', price=100)
        db.session.add_all([f1, f2])
        db.session.commit()

        p1.add_order(f1, 5)
        p2.add_order(f1, 10)
        p2.add_order(f2, 2)
        db.session.commit()
        print(f1.owner_profiles().all())
        self.assertEqual(f1.total_orders(), 15)
        #self.assertEqual(p2.order_quantity(f1).quantity, 10)

if __name__ == '__main__':
    unittest.main(verbosity=2)