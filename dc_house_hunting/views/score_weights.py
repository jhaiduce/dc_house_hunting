from pyramid.view import view_config
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from .residence import ResidenceCRUD
from ..models import Residence, WeightFactor, WeightMapping, SmootherstepMapping
import json

class SmoothstepMapping(colander.MappingSchema):
    lower=colander.SchemaNode(colander.Float())
    upper=colander.SchemaNode(colander.Float())

class FieldWeightSchema(colander.MappingSchema):
    mapping=SmoothstepMapping()
    weight=colander.SchemaNode(colander.Float())

weight_schema=colander.SchemaNode(colander.Mapping())

for field in Residence.score_fields:
    weight_schema.add(FieldWeightSchema(name=field))

def get_appstruct(dbsession):

    appstruct = {}

    for field in Residence.score_fields:
        appstruct[field]={'mapping':{}}
        weightfactor = WeightFactor.get(field, dbsession)
        appstruct[field]['weight'] = weightfactor.weight
        weightmapping = SmootherstepMapping.get(field, dbsession)
        appstruct[field]['mapping']['lower'] = weightmapping.lower
        appstruct[field]['mapping']['upper'] = weightmapping.upper

    return appstruct    

class ScoreWeightViews(object):

    def __init__(self,request):
        self.request=request

    @property
    def weight_form(self):

        schema=weight_schema.bind(
            request=self.request)

        return deform.Form(schema,buttons=['submit'])

    @view_config(route_name='score_weights', renderer='../templates/import.jinja2')
    def edit_weights(self):
    
        form=self.weight_form.render()

        dbsession=self.request.dbsession

        if 'submit' in self.request.params:
            controls=self.request.POST.items()
            try:
                appstruct=self.weight_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(form=e.render())

            for field in Residence.score_fields:
                weightfactor = WeightFactor.get(field, dbsession)
                weightfactor.weight=appstruct[field]['weight']
                weightmapping = SmootherstepMapping.get(field, dbsession)
                weightmapping.lower=appstruct[field]['mapping']['lower']
                weightmapping.upper=appstruct[field]['mapping']['upper']
                dbsession.add(weightfactor)
                dbsession.add(weightmapping)

            redirect_url = self.request.route_url(ResidenceCRUD.routes['list'])

            return HTTPFound(
                redirect_url
            )
    
        form=self.weight_form.render(
            get_appstruct(dbsession)
        )

        return dict(form=form)
