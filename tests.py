import unittest
from main import app, db
from main.models import Profile, Order

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_orders_to_profile(self):
        p1 = Profile(username='sky7021', email='example@testmail.com')
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(p1.orders.all(), [])

        f1 = Order(name='Tenshi', price=35)
        db.session.add(f1)
        db.session.commit()
        p1.add_order(f1)
        self.assertTrue(p1.owns_order(f1))
        self.assertEqual(p1.orders.count(), 1)
        self.assertEqual(p1.orders.first().name, 'Tenshi')

        p1.remove_order(f1)
        db.session.commit()

        self.assertFalse(p1.owns_order(f1))
        self.assertEqual(p1.orders.count(), 0)
    
    def test_order_ownership(self):
        p1 = Profile(username='sky7021', email='example@testmail.com')
        p2 = Profile(username='baldspot', email='example@testmail.com')
        db.session.add_all([p1, p2])

        f1 = Order(name='Cirno', price=50)
        f2 = Order(name='Tenshi', price=100)
        db.session.add_all([f1, f2])
        db.session.commit()

        p1.add_order(f1)
        p2.add_order(f1)
        p2.add_order(f2)
        db.session.commit()

        self.assertEqual(p1.owned_orders().all(), [f1])
        self.assertEqual(p2.owned_orders().all(), [f1, f2])
        self.assertEqual(f1.owner_profiles().all(), [p2, p1])
        self.assertEqual(f2.owner_profiles().all(), [p2])

        db.session.delete(f1)
        self.assertEqual(p1.owned_orders().all(), [])
        self.assertEqual(p2.owned_orders().all(), [f2])
    
    def test_manageprofile(self):
        f1 = Order(name='Cirno', price=50)
        f2 = Order(name='Tenshi', price=100)
        f3 = Order(name='Reimu', price=1)
        f4 = Order(name='Marisad', price=110) 
        db.session.add_all([f1, f2, f3, f4])

        p1 = Profile(username='sky7021')
        p2 = Profile(username='baldspot')
        db.session.add_all([p1, p2])

        for f in [f1, f2, f3, f4]:
            p1.add_order(f)
        db.session.commit()

        all_orders = [(f.name, f.name) for f in Order.query.order_by('name')]
        print(all_orders)
        print(p1.owned_orders().all())

if __name__ == '__main__':
    unittest.main(verbosity=2)