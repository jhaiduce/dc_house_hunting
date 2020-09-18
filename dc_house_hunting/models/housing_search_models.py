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
    Boolean,
    Numeric
)

from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import relationship

from .meta import Base

from datetime import datetime

class Location(Base):

    __tablename__='location'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('location_seq'), primary_key=True)
    street_address=Column(String(255))
    city=Column(String(255))
    state=Column(String(2))
    postal_code=Column(String(5))
    lat = Column(Float)
    lon = Column(Float)
    elevation = Column(Float)

class ResidenceType(Base):

    __tablename__='residencetype'

    id = Column(Integer, Sequence('residencetype_seq'), primary_key=True)
    name=Column(String(255))

class ParkingType(Base):

    __tablename__='parkingtype'

    id = Column(Integer, Sequence('parkingtype_seq'), primary_key=True)
    name=Column(String(255))

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
    parkingtype=relationship(ParkingType,foreign_keys=parkingtype_id)
    bedrooms=Column(Integer)
    bathrooms=Column(Integer)
    half_bathrooms=Column(Integer)
    area=Column(Float)
    lotsize=Column(Float)
    laundry=Column(Boolean)
    laundry_hang_drying=Column(Boolean)
    basement=Column(Boolean)
    attic=Column(Boolean)
    price=Column(Numeric)
    hoa_fee=Column(Numeric)
    taxes=Column(Numeric)
    notes=Column(Text)
    bicycle_storage=Column(Boolean)
    interracial_neighborhood=Column(Boolean)
    kitchen_cabinet_space=Column(Float)
    kitchen_counter_space=Column(Float)
    air_drying_clothes=Column(Boolean)
    coop=Column(Boolean)
    url=Column(Text)

class School(Base):

    __tablename__='school'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('school_seq'), primary_key=True)
    name = Column(String(255))
    location_id=Column(
        Integer,ForeignKey('location.id'))
    location=relationship(Location,foreign_keys=location_id)
    class_size=Column(Float)
    lowest_grade=Column(Integer)
    highest_grade=Column(Integer)

class FoodSourceType(Base):

    __tablename__='foodsourcetype'

    id = Column(Integer, Sequence('foodsourcetype_seq'), primary_key=True)
    name=Column(String(255))

class FoodSource(Base):

    __tablename__='foodsource'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('foodsource_seq'), primary_key=True)

    name=Column(String(255))

    location_id=Column(
        Integer,ForeignKey('location.id'))
    location=relationship(Location,foreign_keys=location_id)
    foodsourcetype_id=Column(
        Integer,ForeignKey('foodsourcetype.id'))
    kind=relationship(FoodSourceType,foreign_keys=foodsourcetype_id)

class Park(Base):

    __tablename__='park'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('park_seq'), primary_key=True)

    location_id=Column(
        Integer,ForeignKey('location.id'))
    location=relationship(Location,foreign_keys=location_id)

    playground=Column(Boolean)
    trees=Column(Boolean)
