import unittest
from unittest.mock import patch
import requests
import configparser
import json
import re
from bs4 import BeautifulSoup
from dc_house_hunting.celery import celery
from celery.result import AsyncResult

def wait_for_celery():
    from dc_house_hunting import celery
    while True:
        try:
            # Check whether there are celery workers running
            worker_status = celery.get_celery_worker_status()
            if worker_status is not None:
                # There are workers, exit the loop
                break
        except IOError:
            print('Broker not running')
            log.debug('Broker not running.')
        else:
            print('No celery workers running.')
            log.debug('No celery workers running.')

        sleep(1)

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.session=requests.Session()
        self.session.verify='/etc/ssl/ca.pem'

        self.config=configparser.ConfigParser()
        self.config.read('/run/secrets/production.ini')

        self.admin_password=self.config['app:main']['admin_password']

        while True:
            try:
                resp=self.session.post('https://localhost.localdomain/login',data={
                    'login':'admin',
                    'password':self.admin_password,
                    'form.submitted':'Log+In'
                })
                if resp.status_code!=200: continue
                break
            except requests.exceptions.ConnectionError:
                print('Connection failed. Sleeping before retry.')
                import time
                time.sleep(2)

        try:
            self.assertEqual(resp.history[0].status_code,302)
        except IndexError:
            print(resp.text)
            raise
        self.assertEqual(resp.history[0].headers['Location'],'https://localhost.localdomain/')

    def tearDown(self):
        resp=self.session.post('https://localhost.localdomain/logout')
        self.assertEqual(resp.history[0].status_code,302)
        self.assertEqual(resp.history[0].headers['Location'],'https://localhost.localdomain/')

        resp=self.session.get('https://localhost.localdomain/residence')
        self.assertEqual(resp.history[0].status_code,302)
        self.assertEqual(resp.history[0].headers['Location'],'https://localhost.localdomain/login?next=https%3A%2F%2Flocalhost.localdomain%2Fresidence')

    def test_residence_crud(self):

        resp=self.session.post(
            'https://localhost.localdomain/residence/new',
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
        resp=self.session.get('https://localhost.localdomain/residence')

        # Check that the new entry is listed
        self.assertIsNotNone(re.search(r'a href="https?://.+/residence/{}/edit"'.format(id),resp.text))

    def test_import_brightmls(self):

        wait_for_celery()

        resp=self.session.post(
            'https://localhost.localdomain/import',
            data={
            'submit':'submit',
            'url':'https://matrix.brightmls.com/Matrix/Public/Portal.aspx?ID=16150598256',
        })

        # Check that we got redirected
        try:
            self.assertEqual(resp.history[0].status_code,302)
        except IndexError:
            print(resp.text)
            raise

        task_result=AsyncResult(
            json.loads(resp.history[0].text)['task_id'],
            app=celery
        )

        result=task_result.wait()

    def test_import_realtor_com(self):

        wait_for_celery()

        resp=self.session.post(
            'https://localhost.localdomain/import',
            data={
                'submit':'submit',
                'url':'https://www.realtor.com/realestateandhomes-detail/2508-36th-Pl-SE_Washington_DC_20020_M61723-48772',
                'content':open('realtor_com_detail_test.html').read()
            })

        # Check that we got redirected
        try:
            self.assertEqual(resp.history[0].status_code,302)
        except IndexError:
            print(resp.text)
            raise

        task_result=AsyncResult(
            json.loads(resp.history[0].text)['task_id'],
            app=celery
        )

        result=task_result.wait()

        resp=self.session.post(
            'https://localhost.localdomain/import',
            headers={
                'Content-Type':'multipart/form-data; boundary=---------------------------350037505235270160363570564592'
            },
            data=('''-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="_charset_"

UTF-8
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="__formid__"

deform
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="url"

https://www.realtor.com/realestateandhomes-detail/2508-36th-Pl-SE_Washington_DC_20020_M61723-48772
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="content"


-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="__start__"

upload:mapping
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="upload"; filename="realtor_com_detail_test.html"
Content-Type: text/html

''' + \

open('realtor_com_detail_test.html','rb').read().decode('latin-1') + \

    '''
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="uid"

29D6UADLFM
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="__end__"

upload:mapping
-----------------------------350037505235270160363570564592
Content-Disposition: form-data; name="submit"

submit
-----------------------------350037505235270160363570564592--
    ''').encode('utf-8')
        )

        # Check that we got redirected
        try:
            self.assertEqual(resp.history[0].status_code,302)
        except IndexError:
            print(resp.text)
            raise

        task_result=AsyncResult(
            json.loads(resp.history[0].text)['task_id'],
            app=celery
        )

        result=task_result.wait()
