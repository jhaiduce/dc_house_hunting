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

from decimal import Decimal

from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

from .meta import Base

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

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
             kwargs['upper'] = 1
        super(SmootherstepMapping, self).__init__(**kwargs)

    __tablename__='smoothstepmapping'

    id = Column(
            Integer,
            ForeignKey('weightmapping.id'),
            primary_key=True)

    lower = Column(Float, default=0, nullable=False)
    upper = Column(Float, default=1, nullable=False)

    def __call__(self,x):
        if self.lower==self.upper:
            if x>self.upper:
                return 1
            else:
                return 0
        x = max(self.lower,min(x,self.upper))
        x = (x-self.lower)/(self.upper-self.lower)
        y = x**3. * (6. * x**2. - 15. * x + 10.)
        return y

    __mapper_args__ = {
        'polymorphic_identity':'smoothstepmapping'
    }

def mortgage_payment(principal, rate, years):
    num_payments=years*12
    monthly_rate=rate/12
    payment = (principal * monthly_rate) / \
        (1-(1+monthly_rate)**(-num_payments))
    return payment

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
    score=Column(Float)

class ParkingTypeMapping(WeightMapping):

    __tablename__='idmapping'

    __table_args__={'mysql_encrypted':'yes'}

    id = Column(
            Integer,
            ForeignKey('weightmapping.id'),
            primary_key=True)

    def __call__(self,parkingtype_id):
        return object_session(self).query(ParkingType).filter(ParkingType.id==parkingtype_id).one().score

    __mapper_args__ = {
        'polymorphic_identity':'idmapping'
    }

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
    taxes_=Column('taxes',Numeric)
    taxes_computed=Column(Numeric)
    mortgage_=Column('mortgage',Numeric)
    insurance_=Column('insurance',Numeric)
    notes=Column(Text)
    bicycle_storage=Column(Boolean)
    interracial_neighborhood=Column(Boolean)
    kitchen_cabinet_space=Column(Float)
    kitchen_counter_space=Column(Float)
    kitchen_score=Column(Float)
    bike_storage_score=Column(Float)
    air_drying_clothes=Column(Boolean)
    coop=Column(Boolean)
    url=Column(Text)
    score_=Column(Float)
    rejected=Column(Boolean,default=False)
    withdrawn=Column(Boolean,default=False)

    score_fields=['bedrooms', 'bathrooms', 'half_bathrooms', 'area', 'kitchen_score', 'bike_storage_score','parkingtype_id']
    score_field_labels={
        'parkingtype_id':'parking',
        'kitchen_score':'kitchen',
        'bike_storage':'bike storage'
    }

    score_mapping_types={
        'kitchen_score': WeightMapping,
        'bike_storage_score': WeightMapping,
        'parkingtype_id': ParkingTypeMapping
    }

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

    @hybrid_property
    def score(self):
        if self.score_ is None:
            self.score_=self.compute_score()

        return self.score_

    @score.expression
    def score(self):
        return self.score_

    @hybrid_property
    def loan_amount(self):
        if self.price is None: return None
        return min(self.price, 778900)

    @hybrid_property
    def downpayment(self):
        return self.price-self.loan_amount

    def update_mortgage(self):
        rate=Decimal(0.025)
        years=int(30)
        if self.loan_amount is None:
            self.mortgage_=None
        else:
            self.mortgage_ = mortgage_payment(self.loan_amount,rate,years)

    @hybrid_property
    def mortgage(self):
        if self.mortgage_ is None:
            self.update_mortgage()
        return self.mortgage_

    @mortgage.expression
    def mortgage(self):
        return self.mortgage_

    def update_taxes(self):
        if self.taxes_ is not None:
            self.taxes_computed = self.taxes_
        else:
            if self.price is None:
                self.taxes_computed=None
            else:
                tax_rate=Decimal(0.0085)
                self.taxes_computed=self.price*tax_rate

    @hybrid_property
    def taxes(self):
        if self.taxes_computed is None:
            self.update_taxes()

        return self.taxes_computed

    @taxes.expression
    def taxes(self):
        return self.taxes_computed

    @hybrid_property
    def insurance(self):
        if self.insurance_ is not None:
            return self.insurance_
        else:
            return Decimal(1500)

    @hybrid_property
    def monthly_cost(self):
        if self.mortgage is None: return None
        hoa_fee = self.hoa_fee if self.hoa_fee else 0
        return self.mortgage+self.taxes/int(12)+self.insurance/int(12) + hoa_fee

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
