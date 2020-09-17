from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy.exc import DBAPIError
from .header import view_with_header

from .. import models

class default_views(object):

    def __init__(self,request):
        self.request=request

    @view_with_header
    @view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
    def my_view(request):
        return {'project': 'DC House Hunting'}
