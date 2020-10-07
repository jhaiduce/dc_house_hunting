from ..models.housing_search_models import Residence, Location, ListingState, ParkingType
from ..celery import celery
from bs4 import BeautifulSoup
import requests

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

import transaction

import requests

from decimal import Decimal
import re

def import_realtor_com_detail(content, url=None, dbsession=None):

    soup=BeautifulSoup(content,features='lxml')

    import json

    data=json.loads(soup.find(id='__NEXT_DATA__').contents[0])
    property_data=data['props']['pageProps']['property']
    address_data=property_data['location']['address']

    details=property_data['details']

    residence = Residence(
        price=property_data['list_price'],
        url=url,
        location=Location(
            street_address=address_data['line'],
            city=address_data['city'],
            state=address_data['state_code'],
            postal_code=address_data['postal_code'],
            lat=address_data['coordinate']['lat'],
            lon=address_data['coordinate']['lon']
        ),
        bedrooms=property_data['description']['beds'],
        bathrooms=property_data['description']['baths_full'],
        half_bathrooms=property_data['description']['baths_half'],
        area=property_data['description']['sqft'],
        lotsize=property_data['description']['lot_sqft']/43560,
    )

    if property_data['status']=='for_sale':
        residence.listingstate=dbsession.query(ListingState).filter(ListingState.name=='Active').one()

    if property_data['description']['garage']:
        residence.parking=dbsession.query(ParkingType).filter(ParkingType.name=='Private garage').one()
    else:
        try:
            parking_text=next(section['text'] for section in details.property_data if section['category']=='Garage and Parking')
        except StopIteration:
            pass
        else:
            if any(['carport' in text.lower() for text in parking_text]):
                residence.parking=dbsession.query(ParkingType).filter(ParkingType.name=='Carport').one()
            elif any(['driveway' in text.lower() for text in parking_text]):
                residence.parking=dbsession.query(ParkingType).filter(ParkingType.name=='Driveway').one()

    return residence

def import_realtor_com(content, url, dbsession=None):
    from urllib.parse import urlparse

    parsed_url=urlparse(url)

    if parsed_url.path.startswith('/realestateandhomes-detail'):
        return import_realtor_com_detail(content, url, dbsession)

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
        bathrooms_span=bathroom_str=numbers_row.findChildren('span')[2]
        if len(bathrooms_span.contents)>0:
            bathroom_str=numbers_row.findChildren('span')[2].contents[0]
            bathroom_arr=[int(i) for i in bathroom_str.split('/')]
            bathrooms=bathroom_arr[0]
            if len(bathroom_arr)>1:
                halfbaths=bathroom_arr[1]
            else:
                halfbaths=0
        else:
            bathrooms=None
            halfbaths=None
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
def import_from_url(url,content=None):

    from ..celery import session_factory
    from ..models import get_tm_session

    tm=transaction.manager

    dbsession=get_tm_session(session_factory, tm)

    logger.debug('Received import task for URL {}'.format(url))

    from urllib.parse import urlparse

    parsed_url=urlparse(url)

    hostname=parsed_url.hostname

    if content is None:
        content=requests.get(url).content

    if hostname.endswith('brightmls.com'):
        objects=import_brightmls(content,url,dbsession)
    elif hostname.endswith('realtor.com'):
        objects=import_realtor_com(content,url,dbsession)

    for obj in objects:
        dbsession.add(obj)

    def submit_update_score_task(success,residence_ids):
        from .scores import update_scores
        result=update_scores.delay(residence_ids)

    dbsession.flush()

    tm.get().addAfterCommitHook(
        submit_update_score_task,
        args=[[obj.id for obj in objects if isinstance(obj,Residence)]])

    transaction.commit()
