import unittest
from main import app, db
from main.models import Profile, Fumo

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_fumos_to_profile(self):
        p1 = Profile(username='sky7021')
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(p1.fumos.all(), [])

        f1 = Fumo(name='Tenshi', price=35)
        db.session.add(f1)
        db.session.commit()
        p1.add_fumo(f1)
        self.assertTrue(p1.owns_fumo(f1))
        self.assertEqual(p1.fumos.count(), 1)
        self.assertEqual(p1.fumos.first().name, 'Tenshi')

        p1.remove_fumo(f1)
        db.session.commit()

        self.assertFalse(p1.owns_fumo(f1))
        self.assertEqual(p1.fumos.count(), 0)
    
    def test_fumo_ownership(self):
        p1 = Profile(username='sky7021')
        p2 = Profile(username='baldspot')
        db.session.add_all([p1, p2])

        f1 = Fumo(name='Cirno', price=50)
        f2 = Fumo(name='Tenshi', price=100)
        db.session.add_all([f1, f2])
        db.session.commit()

        p1.add_fumo(f1)
        p2.add_fumo(f1)
        p2.add_fumo(f2)
        db.session.commit()

        self.assertEqual(p1.owned_fumos().all(), [f1])
        self.assertEqual(p2.owned_fumos().all(), [f1, f2])
        self.assertEqual(f1.owner_profiles().all(), [p2, p1])
        self.assertEqual(f2.owner_profiles().all(), [p2])

        db.session.delete(f1)
        self.assertEqual(p1.owned_fumos().all(), [])
        self.assertEqual(p2.owned_fumos().all(), [f2])
    
    def test_manageprofile(self):
        f1 = Fumo(name='Cirno', price=50)
        f2 = Fumo(name='Tenshi', price=100)
        f3 = Fumo(name='Reimu', price=1)
        f4 = Fumo(name='Marisad', price=110) 
        db.session.add_all([f1, f2, f3, f4])

        p1 = Profile(username='sky7021')
        p2 = Profile(username='baldspot')
        db.session.add_all([p1, p2])

        for f in [f1, f2, f3, f4]:
            p1.add_fumo(f)
        db.session.commit()

        all_fumos = [(f.name, f.name) for f in Fumo.query.order_by('name')]
        print(all_fumos)
        print(p1.owned_fumos().all())

if __name__ == '__main__':
    unittest.main(verbosity=2)