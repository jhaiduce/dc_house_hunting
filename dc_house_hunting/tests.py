import unittest
from unittest.mock import Mock

from pyramid import testing

import transaction

import json

from decimal import Decimal

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

        request.tm=Mock()

        views=ResidenceCRUD(request)

        resp=views.edit()

        self.assertEqual(resp.status_code,302)
        residence_id=json.loads(resp.text)['id']

        residence=self.session.query(Residence).filter(Residence.id==residence_id).one()

        self.assertEqual(residence.parkingtype_id,1)
        self.assertEqual(residence.residencetype_id,1)
        self.assertEqual(residence.location.postal_code,'12345')
        self.assertEqual(residence.location.street_address,'123 Main')
        self.assertIsNone(residence.monthly_cost)

        residence.price=Decimal(800000)

        self.assertAlmostEqual(float(residence.monthly_cost),3769.26,2)

        request=testing.DummyRequest(dbsession=self.session)
        views=ResidenceCRUD(request)
        resp=views.list()

        # Check that the new entry is listed
        self.assertIn(residence,resp['items'])

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

        self.session.add(residence)

        self.assertEqual(residence.score,1)

    def test_edit_weights(self):

        from .models import Residence, WeightFactor, WeightMapping
        from .views.score_weights import ScoreWeightViews

        reqdata={
            'submit':'submit',
            'bedrooms':{
                'weight':'1',
                'mapping':{'lower':'0','upper':'5'}
            },
            'bathrooms':{
                'weight':'1',
                'mapping':{'lower':'0','upper':'2'}
            },
            'half_bathrooms':{
                'weight':'1',
                'mapping':{'lower':'0','upper':'2'}
            },
            'half_bathrooms':{
                'weight':'1',
                'mapping':{'lower':'0','upper':'2'}
            },
            'area':{
                'weight':'1',
                'mapping':{'lower':'1000','upper':'2000'}
            },
            'kitchen_score':{'weight':'1'},
            'bike_storage_score':{'weight':'1'},
            'parkingtype_id':{'weight':'1'},
        }

        request=testing.DummyRequest(
            params=reqdata, dbsession=self.session)

        views=ScoreWeightViews(request)

        resp=views.edit_weights()

        self.assertEqual(resp.status_code,302)

        self.assertAlmostEqual(
            WeightFactor.get('bedrooms',self.session).weight, 1)
        self.assertAlmostEqual(
            WeightMapping.get('area',self.session).upper,2000)

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
