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
from sqlalchemy.orm.session import object_session

from .meta import Base

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

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
    score_=Column(Float)

    score_fields=['bedrooms', 'bathrooms', 'half_bathrooms', 'area']

    def get_score_component(self,field,session=None):
        if session is None:
            session=object_session(self)
        return WeightFactor.get(field,session) * WeightMapping.get(field,session)(getattr(self,field))

    def compute_score(self):
        score=0

        for field in self.score_fields:
            if getattr(self,field) is not None:
                score += self.get_score_component(field)

        self.score_ = score

        return score

    @property
    def score(self):
        if self.score_ is None:
            self.score_=self.compute_score()

        return self.score_

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

class WeightFactor(Base):

    __tablename__='weightfactor'

    __table_args__={'mysql_encrypted':'yes'}

    def __init__(self, **kwargs):
        if 'weight' not in kwargs:
             kwargs['weight'] = 1
        super(WeightFactor, self).__init__(**kwargs)

    id = Column(Integer, Sequence('weightfactor_seq'), primary_key=True)

    name = Column(String(255), unique=True, nullable=False)
    weight = Column(Float, default=1, nullable=False)

    def __mul__(self,other):
        return self.weight*other

    @classmethod
    def get(cls,name,session):
        try:
            return session.query(WeightFactor).filter(
                    WeightFactor.name==name).one()
        except NoResultFound:
            # Return a new generic mapping
            return cls(name=name)

class WeightMapping(Base):

    __tablename__='weightmapping'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(Integer, Sequence('weightmapping_seq'), primary_key=True)

    name = Column(String(255), unique=True, nullable=False)
    kind = Column(String(255), nullable=False)

    def __call__(self,x):
        return x

    __mapper_args__ = {
        'polymorphic_on': kind,
        'polymorphic_identity':'weightmapping'
    }

    @classmethod
    def get(cls,name,session):
        try:
            return session.query(WeightMapping).filter(WeightMapping.name==name).one()
        except NoResultFound:
            # Return a new generic mapping
            return cls(name=name)

class FactorMapping(WeightMapping):

    def __init__(self, **kwargs):
        if 'factor' not in kwargs:
             kwargs['factor'] = 1
        super(FactorMapping, self).__init__(**kwargs)

    __tablename__='factormapping'

    id = Column(
            Integer,
            ForeignKey('weightmapping.id'),
            primary_key=True)

    factor = Column(Float, default=1, nullable=False)

    def __call__(self,x):
        return x*self.factor

    __mapper_args__ = {
        'polymorphic_identity':'factormapping'
    }

class SmootherstepMapping(WeightMapping):

    def __init__(self,**kwargs):
        if 'lower' not in kwargs:
             kwargs['lower'] = 0
        if 'upper' not in kwargs:
             kwargs['upper'] = 0
        super(SmootherstepMapping, self).__init__(**kwargs)

    __tablename__='smoothstepmapping'

    id = Column(
            Integer,
            ForeignKey('weightmapping.id'),
            primary_key=True)

    lower = Column(Float, default=0, nullable=False)
    upper = Column(Float, default=1, nullable=False)

    def __call__(self,x):
        x = max(self.lower,min(x,self.upper))
        x = (x-self.lower)/(self.upper-self.lower)
        y = x**3. * (6. * x**2. - 15. * x + 10.)
        return y

    __mapper_args__ = {
        'polymorphic_identity':'smoothstepmapping'
    }
