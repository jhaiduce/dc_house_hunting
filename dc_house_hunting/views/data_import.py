from pyramid.view import view_config
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from .residence import ResidenceCRUD
import json

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""

    def preview_url(self, uid):
        return None

@colander.deferred
def get_file_upload_widget(node, kw):
    return deform.widget.FileUploadWidget(kw['tmpstore'])

class ImportForm(colander.MappingSchema):

    url=colander.SchemaNode(colander.String())
    content=colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(), missing=None)
    upload=colander.SchemaNode(
        deform.FileData(),
        widget=get_file_upload_widget, missing=None)

class ImportViews(object):

    def __init__(self,request):
        self.request=request

    @property
    def tmpstore(self):
        return MemoryTmpStore()

    @property
    def import_form(self):

        schema=ImportForm().bind(
            request=self.request,
            tmpstore=self.tmpstore
        )

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

            if appstruct['content'] or appstruct['upload']:

                if appstruct['content']:
                    content=appstruct['content']
                elif appstruct['upload']:
                    content=appstruct['upload']['fp'].read().decode('cp437')
            else:
                content=None

            result=import_from_url.delay(appstruct['url'], content)

            redirect_url=self.request.route_url(ResidenceCRUD.routes['list'])

            return HTTPFound(
                redirect_url,
                content_type='application/json',
                charset='',
                text=json.dumps(
                    {'task_id':result.task_id})
            )

        return dict(form=form)
