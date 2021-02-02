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

        from .models.housing_search_models import ParkingType, ListingState, ResidenceType

        self.session.add(ResidenceType(id=1,name='House'))
        self.session.add(ResidenceType(id=2,name='Townhouse'))

        self.session.add(ParkingType(id=1,name='Street'))
        self.session.add(ParkingType(id=2,name='Private garage'))
        self.session.add(ParkingType(id=3,name='Driveway'))
        self.session.add(ParkingType(id=4,name='Carport'))

        self.session.add(ListingState(id=1,name='Active'))
        self.session.add(ListingState(id=2,name='Closed'))
        self.session.add(ListingState(id=3,name='Withdrawn'))

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

        from .models.housing_search_models import Residence
        from .models.housing_search_models import ResidenceType
        from .models.housing_search_models import ParkingType
        from .models.housing_search_models import ListingState
        from .models.housing_search_models import Location

        self.session.add(Residence(
            id=1,
            location=Location(
                street_address='123 1st St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=False,
            seen=True,
            listingstate_id=1,
        ))

        self.session.add(Residence(
            id=2,
            location=Location(
                street_address='123 2nd St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=None,
            seen=None,
            listingstate_id=None,
        ))

        self.session.add(Residence(
            id=3,
            location=Location(
                street_address='123 3rd St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=False,
            seen=None,
            listingstate_id=2,
            price=Decimal(600000),
        ))

        self.session.add(Residence(
            id=4,
            location=Location(
                street_address='123 4th St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=False,
            seen=False,
            listingstate_id=1,
            price=Decimal(820000),
        ))

        self.session.add(Residence(
            id=5,
            location=Location(
                street_address='123 5th St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=True,
            seen=True,
            listingstate_id=1,
            price=Decimal(700000),
        ))

        self.session.add(Residence(
            id=6,
            location=Location(
                street_address='123 6th St',
                city='Washington',
                state='DC',
                postal_code='20003'
            ),
            rejected=False,
            seen=True,
            listingstate_id=1,
            price=Decimal(700000),
        ))

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

        self.session.delete(residence)

    def test_list_filters(self):

        from .views.residence import ResidenceCRUD
        from .models import Residence

        request=testing.DummyRequest(dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.list()

        self.assertIn(1,[item.id for item in resp['items']])
        self.assertIn(2,[item.id for item in resp['items']])
        self.assertNotIn(3,[item.id for item in resp['items']])
        self.assertIn(4,[item.id for item in resp['items']])
        self.assertNotIn(5,[item.id for item in resp['items']])
        self.assertIn(6,[item.id for item in resp['items']])

        from webob.multidict import MultiDict

        request=testing.DummyRequest(
            params=MultiDict((
                ('__start__','price:mapping'),
                ('min',''),
                ('max','800000'),
                ('__end__','price:mapping')
            )),
            dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.list()

        self.assertNotIn(1,[item.id for item in resp['items']])
        self.assertNotIn(2,[item.id for item in resp['items']])
        self.assertNotIn(3,[item.id for item in resp['items']])
        self.assertNotIn(4,[item.id for item in resp['items']])
        self.assertNotIn(5,[item.id for item in resp['items']])
        self.assertIn(6,[item.id for item in resp['items']])

        request=testing.DummyRequest(
            params=MultiDict((
                ('__start__','price:mapping'),
                ('min',''),
                ('max','800000'),
                ('__end__','price:mapping'),
                ('listingstate','any')
            )),
            dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.list()

        self.assertNotIn(1,[item.id for item in resp['items']])
        self.assertNotIn(2,[item.id for item in resp['items']])
        self.assertIn(3,[item.id for item in resp['items']])
        self.assertNotIn(4,[item.id for item in resp['items']])
        self.assertNotIn(5,[item.id for item in resp['items']])
        self.assertIn(6,[item.id for item in resp['items']])

        request=testing.DummyRequest(
            params=MultiDict((
                ('listingstate','any'),
            )),
            dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.list()

        self.assertIn(1,[item.id for item in resp['items']])
        self.assertIn(2,[item.id for item in resp['items']])
        self.assertIn(3,[item.id for item in resp['items']])
        self.assertIn(4,[item.id for item in resp['items']])
        self.assertNotIn(5,[item.id for item in resp['items']])
        self.assertIn(6,[item.id for item in resp['items']])

        request=testing.DummyRequest(
            params=MultiDict((
                ('rejected','true'),
            )),
            dbsession=self.session)

        views=ResidenceCRUD(request)

        resp=views.list()

        self.assertNotIn(1,[item.id for item in resp['items']])
        self.assertNotIn(2,[item.id for item in resp['items']])
        self.assertNotIn(3,[item.id for item in resp['items']])
        self.assertNotIn(4,[item.id for item in resp['items']])
        self.assertIn(5,[item.id for item in resp['items']])
        self.assertNotIn(6,[item.id for item in resp['items']])

class ScoreTests(BaseTest):

    def test_smoothstep_mapping(self):

        from .models import SmootherstepMapping

        self.assertAlmostEqual(SmootherstepMapping(lower=0,upper=1)(0.5),0.5)
        self.assertAlmostEqual(SmootherstepMapping(lower=0,upper=1)(1.5),1)
        self.assertAlmostEqual(SmootherstepMapping(lower=0,upper=1)(-0.5),0)
        self.assertAlmostEqual(SmootherstepMapping(lower=1,upper=0)(0.5),0.5)
        self.assertAlmostEqual(SmootherstepMapping(lower=1,upper=0)(1.5),0)
        self.assertAlmostEqual(SmootherstepMapping(lower=1,upper=0)(-0.5),1)

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
            'monthly_cost':{
                'weight':'1',
                'mapping':{'lower':'4100','upper':'2000'}
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

    def test_import_realtor_com(self):
        from .tasks.data_import import import_realtor_com_detail
        residence=import_realtor_com_detail(open('realtor_com_detail_test.html').read(),dbsession=self.session)
        self.assertEqual(residence.price,Decimal(679000))
        self.assertEqual(residence.location.street_address,'2508 36th Pl SE')
        self.assertEqual(residence.listingstate.name,'Active')
        self.assertEqual(residence.bedrooms,3)
        self.assertEqual(residence.bathrooms,3)
        self.assertAlmostEqual(residence.lotsize, 0.109045, places=6)
        self.assertAlmostEqual(residence.area, 2256, places=1)
        self.assertEqual(residence.parking.name,'Private garage')

        residence=import_realtor_com_detail(open('realtor_com_detail_test1.html').read(),dbsession=self.session)
        self.assertEqual(residence.price,Decimal(669000))
        self.assertEqual(residence.location.street_address,'3823 Pope St SE')
        self.assertEqual(residence.listingstate.name,'Active')
        self.assertEqual(residence.bedrooms,5)
        self.assertEqual(residence.bathrooms,3)
        self.assertAlmostEqual(residence.lotsize, 0.1184573, places=6)
        self.assertAlmostEqual(residence.area, 2596, places=1)
        self.assertEqual(residence.parking.name,'Driveway')

        residence=import_realtor_com_detail(open('realtor_com_detail_test2.html').read(),dbsession=self.session)
        self.assertEqual(residence.price,Decimal(769000))
        self.assertEqual(residence.location.street_address,'251 G St SW Unit 113')
        self.assertEqual(residence.listingstate.name,'Active')
        self.assertEqual(residence.bedrooms,3)
        self.assertEqual(residence.bathrooms,2)
        self.assertIsNone(residence.lotsize)
        self.assertAlmostEqual(residence.area, 1513, places=1)
        self.assertIsNone(residence.parkingtype)

    def test_import_view(self):
        from .views.data_import import ImportViews
        from cgi import FieldStorage

        request=testing.DummyRequest(post={
            'submit':'submit',
            'url':'https://www.realtor.com/realestateandhomes-detail/2508-36th-Pl-SE_Washington_DC_20020_M61723-48772',
            'upload':{'fh':open('realtor_com_detail_test.html')}
        },dbsession=self.session)

        views=ImportViews(request)

        resp=views.import_residences()

        request=testing.DummyRequest(post={
            'submit':'submit',
            'url':'https://www.realtor.com/realestateandhomes-detail/2508-36th-Pl-SE_Washington_DC_20020_M61723-48772',
            'content':open('realtor_com_detail_test.html').read()
        },dbsession=self.session)

        views=ImportViews(request)

        resp=views.import_residences()
