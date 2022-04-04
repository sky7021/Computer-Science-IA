import unittest, datetime
from main import create_app, db
from main.models import Profile, Order, LinkOrder
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
        
        #Cirno and Tenshi added to sky7021
        p1.add_order(f1, 5, datetime.date(2020, 5, 17))
        p1.add_order(f2, 15, datetime.date(2020, 5, 17))
        
        #Cirno and Tenshi added to baldspot
        p2.add_order(f1, 10, datetime.date(2020, 5, 17))
        p2.add_order(f2, 2, datetime.date(2020, 5, 17))
        db.session.commit()

        #sky7021's order of Cirno on 2020/5/17 gets updated to 20
        p1.modify_quantity(f1, 20, datetime.date(2020, 5, 17))
        db.session.commit()
        self.assertEqual(p1.get_order(f1, datetime.date(2020, 5, 17)).quantity, 20)

        #name changed from Cirno to Aya and price to 10
        f1.name = 'Aya' 
        f1.price = 10
        db.session.commit()
        p1_order_f1 = p1.get_order(f1, datetime.date(2020, 5, 17)).order
        self.assertEqual(p1_order_f1.name, 'Aya')
        self.assertEqual(p1_order_f1.price, 10)

        p1.remove_order(f1, datetime.date(2020, 5, 17))
        db.session.commit()
        self.assertEqual(p1.owned_orders(datetime.date(2020, 5, 17)), [f2])


#tested: total_orders, get_order
if __name__ == '__main__':
    unittest.main(verbosity=2)