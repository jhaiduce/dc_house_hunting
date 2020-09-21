import unittest

from pyramid import testing

import transaction

import json

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        self.config.include('pyramid_jinja2')
        self.config.include('.routes')
        self.config.scan()
        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.init_database()

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

class TestCRUD(BaseTest):

    def setUp(self):
        super(TestCRUD, self).setUp()

        from .models.housing_search_models import ResidenceType
        from .models.housing_search_models import ParkingType

        self.session.add(ResidenceType(id=1,name='House'))
        self.session.add(ParkingType(id=1,name='Street'))

    def test_residence(self):

        from .views.residence import ResidenceCRUD
        from .models import Residence

        request=testing.DummyRequest(post={
            'save_close':'save_close',
            'address':'123 Main',
            'zip':'12345',
            'basement':'true',
            'bathrooms':'2',
            'bedrooms':'2',
            'city':'Washington',
            'parkingtype':'1',
            'residencetype':'1',
            'state':'DC',
            'notes':'',
            'price':''
        },dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.edit()

        self.assertEqual(resp.status_code,302)
        residence_id=json.loads(resp.text)['id']

        residence=self.session.query(Residence).filter(Residence.id==residence_id).one()

        self.assertEqual(residence.parkingtype_id,1)
        self.assertEqual(residence.residencetype_id,1)
        self.assertEqual(residence.location.postal_code,'12345')
        self.assertEqual(residence.location.street_address,'123 Main')

class ScoreTests(BaseTest):

    def test_get_score(self):

        from .models import Residence, Location

        residence=Residence(
            location=Location(
                street_address='123 1st St',
                city='Washington',
                state='DC'
            ),
            bedrooms=1,
        )

        score=residence.get_score(self.session)
        self.assertEqual(score,1)

class AuthenticationTests(BaseTest):

    def setUp(self):
        super(AuthenticationTests, self).setUp()

        from .models import User

        user=User(
            name='admin'
        )

        user.set_password('password')
        self.session.add(user)

    def test_check_password(self):
        from .models import User

        user=self.session.query(User).filter(User.name=='admin').one()

        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('pa$$word'))

class DataImportTests(BaseTest):

    def test_import_brightmls(self):

        from .tasks.data_import import import_brightmls
        import_brightmls(open('brightmls_testdata.html').read())
