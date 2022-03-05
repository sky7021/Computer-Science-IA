import unittest
from main import app, db
from main.models import Profile, Order, OrderQuantity

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    #tests adding and removing a single Order with quantity to profile
    def test_orders_to_profile(self):
        p1 = Profile(username='sky7021', email='example@testmail.com')
        db.session.add(p1)
        db.session.commit()

        f1 = Order(name='Tenshi', price=35)
        db.session.add(f1)
        p1.add_order(f1, 3)
        db.session.commit()
        print(p1.quantities)
        self.assertEqual(p1.order_quantity(f1).quantity, 3)

        p1.remove_order(f1)
        db.session.commit()
        print(p1.quantities)
        self.assertEqual(p1.quantities, [])

    #add quantities of same item to different profiles 
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

        self.assertEqual(p1.order_quantity(f1).quantity, 5)
        self.assertEqual(p2.order_quantity(f1).quantity, 10)

        p2.modify_order(f1, 5)
        db.session.commit()
        self.assertEqual(p2.order_quantity(f1).quantity, 5)

#real life scenario with multiple users and orders being added check values
    def test_manageprofile(self):
        f1 = Order(name='Cirno', price=50)
        f2 = Order(name='Tenshi', price=100)
        f3 = Order(name='Reimu', price=1)
        f4 = Order(name='Marisad', price=str(110)) 
        db.session.add_all([f1, f2, f3, f4])

        p1 = Profile(username='sky7021', email='example1@testmail.com')
        p2 = Profile(username='baldspot', email='example2@testmail.com')
        db.session.add_all([p1, p2])

        p1.add_order(f1, 10)
        q = p1.order_quantity(f1).quantity * f1.price
        self.assertEqual(q, 500)

        p1.modify_order(f1, 5)
        q = p1.order_quantity(f1).quantity * f1.price
        self.assertEqual(q, 250)



if __name__ == '__main__':
    unittest.main(verbosity=2)