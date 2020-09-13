from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    DateTime,
    Float,
    ForeignKey,
    Sequence,
    Date,
    Boolean
)

from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import relationship

from .meta import Base

from datetime import datetime

class Location(Base):

    __tablename__='location'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('location_seq'), primary_key=True)
    street_address=Column(String)
    city=Column(String)
    state=Column(String(2))
    postal_code=Column(String(5))
    lat = Column(Float)
    lon = Column(Float)
    elevation = Column(Float)

class ResidenceType(Base):

    __tablename__='residencetype'

    id = Column(Integer, Sequence('residencetype_seq'), primary_key=True)
    name=Column(String)

class ParkingType(Base):

    __tablename__='parkingtype'

    id = Column(Integer, Sequence('parkingtype_seq'), primary_key=True)
    name=Column(String)

class Residence(Base):

    __tablename__='residence'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('residence_seq'), primary_key=True)
    location_id=Column(
        Integer,ForeignKey('location.id'))
    location=relationship(Location,foreign_keys=location_id)
    residencetype_id=Column(
        Integer,ForeignKey('residencetype.id'))
    residencetype=relationship(ResidenceType,foreign_keys=residencetype_id)
    parkingtype_id=Column(
        Integer,ForeignKey('parkingtype.id'))
    bedrooms=Column(Integer)
    bathrooms=Column(Integer)
    area=Column(Float)
    laundry=Column(Boolean)
    basement=Column(Boolean)
    price_=Column(Integer)
    notes=Column(String)

    @hybrid_property
    def price(self):

        if self.price_ is None:
            return None

        else:
            return price/100

    @price.setter
    def price(self,new_price):

        self.price_=new_price*100

    @price.expression
    def price(cls):
        return cls.price_

    @price.update_expression
    def price(cls,new_price):
        return [
            (cls.price_, new_price)
        ]

class School(Base):

    __tablename__='school'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('school_seq'), primary_key=True)
    location_id=Column(
        Integer,ForeignKey('location.id'))
    location=relationship(Location,foreign_keys=location_id)
