from pyramid.view import view_config
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from .residence import ResidenceCRUD
import json

class ImportForm(colander.MappingSchema):

    url=colander.SchemaNode(colander.String())

class ImportViews(object):

    def __init__(self,request):
        self.request=request

    @property
    def import_form(self):

        schema=ImportForm().bind(
            request=self.request)

        return deform.Form(schema,buttons=['submit'])

    @view_config(route_name='import', renderer='../templates/import.jinja2')
    def import_residences(self):
    
        form=self.import_form.render()

        dbsession=self.request.dbsession

        if 'submit' in self.request.params:
            controls=self.request.POST.items()
            try:
                appstruct=self.import_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(form=e.render())

            from ..tasks.data_import import import_from_url
            result=import_from_url.delay(appstruct['url'])

            redirect_url=ResidenceCRUD.routes['list']

            return HTTPFound(
                redirect_url,
                content_type='application/json',
                charset='',
                text=json.dumps(
                    {'task_id':result.task_id})
            )

        return dict(form=form)
