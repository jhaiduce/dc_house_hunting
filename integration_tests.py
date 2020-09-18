import unittest
from unittest.mock import patch
import requests
import configparser
import json
import re
from bs4 import BeautifulSoup

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.session=requests.Session()

        self.config=configparser.ConfigParser()
        self.config.read('/run/secrets/production.ini')

        self.admin_password=self.config['app:main']['admin_password']

        while True:
            try:
                resp=self.session.post('http://web/login',data={
                    'login':'admin',
                    'password':self.admin_password,
                    'form.submitted':'Log+In'
                })
                break
            except requests.exceptions.ConnectionError:
                print('Connection failed. Sleeping before retry.')
                import time
                time.sleep(2)

        self.assertEqual(resp.history[0].status_code,302)
        self.assertEqual(resp.history[0].headers['Location'],'http://web/')

    def tearDown(self):
        resp=self.session.post('http://web/logout')
        self.assertEqual(resp.history[0].status_code,302)
        self.assertEqual(resp.history[0].headers['Location'],'http://web/')

        resp=self.session.get('http://web/residence')
        self.assertEqual(resp.history[0].status_code,302)
        self.assertEqual(resp.history[0].headers['Location'],'http://web/login?next=http%3A%2F%2Fweb%2Fresidence')

    def test_residence_crud(self):

        resp=self.session.post(
            'http://web/residence/new',
            data={
            'save_close':'save_close',
            'address':'123 Main',
            'zip':'12345',
            'basement':'true',
            'bathrooms':'2',
            'bedrooms':'2',
            'city':'Washington',
            'parkingtype':'',
            'residencetype':'',
            'state':'DC',
            'notes':'',
            'price':''
        })

        # Check that we got redirected
        try:
            self.assertEqual(resp.history[0].status_code,302)
        except IndexError:
            print(resp.text)
            raise

        # Get the id of the new entry
        submission_metadata=json.loads(resp.history[0].text)
        id=submission_metadata['id']

        # Load the residence listing page
        resp=self.session.get('http://web/residence')

        # Check that the new entry is listed
        self.assertIsNotNone(re.search(r'a href="https?://.+/residence/{}/edit"'.format(id),resp.text))
