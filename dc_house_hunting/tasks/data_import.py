from ..models.housing_search_models import Residence, Location
from ..celery import celery
from bs4 import BeautifulSoup
import requests

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

import transaction

import requests

from decimal import Decimal
import re

def import_brightmls(content,url=None,dbsession=None):
    
    soup=BeautifulSoup(content,features='lxml')
    
    resultslist=soup.find('div',class_='j-resultsPageAsyncDisplays')
    
    residences=[]
    
    entries=resultslist.find_all('div',class_='d-wrapperTable')
    
    for entry in entries:
    
        rows=entry.div.findChildren('div',class_='row')
        price=Decimal(
        rows[0].div.span.contents[0].replace(
            '$',''
        ).replace(
            ',',''
        ))
        row1_divs=rows[1].findChildren('div')
        
        address=row1_divs[0].span.a.contents[0]
        muni_str=row1_divs[1].span.contents[0]
        match=re.match(r'(?P<city>[a-zA-Z ]+), (?P<state>[A-Z]{2}) (?P<zip>\d{5})',muni_str)
        city=match.group('city')
        state=match.group('state')
        zipcode=match.group('zip')
        
        bedrooms=int(
            row1_divs[3].div.div.span.contents[0])
       
        numbers_row=row1_divs[3]
        bathroom_str=numbers_row.findChildren('span')[2].contents[0]
        bathroom_arr=[int(i) for i in bathroom_str.split('/')]
        bathrooms=bathroom_arr[0]
        if len(bathroom_arr)>1:
            halfbaths=bathroom_arr[1]
        else:
            halfbaths=0
        floorspace=float(numbers_row.findChildren('span')[4].contents[0].replace(',',''))
        try:
            lotsize=float(numbers_row.findChildren('span')[6].contents[0].replace(',',''))
        except IndexError:
            lotsize=None

        new_residence=Residence(
            location=Location(
                street_address=address,
                city=city,
                state=state,
                postal_code=zipcode),
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            half_bathrooms=halfbaths,
            area=floorspace,
            lotsize=lotsize,
            price=price,
            url=url)

        if dbsession is not None:
            existing_residences=dbsession.query(Residence
            ).filter(Residence.location.has(Location.street_address==address)
            ).filter(Residence.location.has(Location.city==city)
            ).filter(Residence.location.has(Location.state==state))
            if existing_residences.count():
                continue

        residences.append(new_residence)
            
    return residences

@celery.task(ignore_result=False)
def import_from_url(url):

    from ..celery import session_factory
    from ..models import get_tm_session

    dbsession=get_tm_session(session_factory, transaction.manager)

    logger.debug('Received import task for URL {}'.format(url))

    from urllib.parse import urlparse

    parsed_url=urlparse(url)

    hostname=parsed_url.hostname

    content=requests.get(url).content

    if hostname.endswith('brightmls.com'):
        objects=import_brightmls(content,url,dbsession)

    from .scores import update_scores

    update_scores.delay([obj.id for obj in objects if isinstance(obj,Residence)])

    for obj in objects:
        dbsession.add(obj)

    transaction.commit()
