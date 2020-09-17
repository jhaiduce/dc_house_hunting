from pyramid.events import subscriber
from .crud import CRUDView, ViewDbInsertEvent,ViewDbUpdateEvent
from ..models import Residence
from colanderalchemy import SQLAlchemySchemaNode
import colander
import deform

@colander.deferred
def get_parkingtype_widget(node,kw):
    from ..models import ParkingType
    dbsession=kw['request'].dbsession
    parkingtypes=dbsession.query(ParkingType)
    choices=[('','')]+[(parkingtype.id, parkingtype.name) for parkingtype in parkingtypes]
    return deform.widget.SelectWidget(values=choices)

@colander.deferred
def get_residencetype_widget(node,kw):
    from ..models import ResidenceType
    dbsession=kw['request'].dbsession
    residencetypes=dbsession.query(ResidenceType)
    choices=[('','')]+[(residencetype.id, residencetype.name) for residencetype in residencetypes]
    return deform.widget.SelectWidget(values=choices)

@subscriber(ViewDbInsertEvent, ViewDbUpdateEvent)
def finalize_residence_fields(event):

    from ..models import Location

    """
    Post-process an automatically deserialized Residence object
    """

    if isinstance(event.obj,Residence):

        # Update the location field
        if event.obj.location is None:
            event.obj.location=Location()

        event.obj.location.street_address=event.appstruct['address']
        event.obj.location.city=event.appstruct['city']
        if event.appstruct['state']:
            event.obj.location.state=event.appstruct['state']
        if event.appstruct['zip']:
            event.obj.location.postal_code=event.appstruct['zip']

        event.obj.parkingtype_id=event.appstruct['parkingtype']
        event.obj.residencetype_id=event.appstruct['residencetype']

class ResidenceCRUD(CRUDView):

    model=Residence
    schema=SQLAlchemySchemaNode(
        Residence,
        includes=[
            colander.SchemaNode(
                colander.String(),
                name='address'),
            colander.SchemaNode(
                colander.String(),
                name='city'),
            colander.SchemaNode(
                colander.String(),
                name='state'),
            colander.SchemaNode(
                colander.String(),
                name='zip',
                missing=None),
            colander.SchemaNode(
                colander.Integer(),
                name='residencetype',
                title='Residence type',
                widget=get_residencetype_widget,
                missing=None
            ),
            'bedrooms',
            'bathrooms',
            'half_bathrooms',
            'laundry',
            'laundry_hang_drying',
            'basement',
            'attic',
            'price',
            'coop',
            colander.SchemaNode(
                colander.Integer(),
                name='parkingtype',
                title='Parking',
                widget=get_parkingtype_widget,
                missing=None
            ),
            'notes',
            'url',
        ],
        overrides={
            'price':{
                'schema':colander.SchemaNode(
                    colander.Decimal('0.01'),
                ),
            },
            'notes':{
                'widget':deform.widget.TextAreaWidget()
            }
        }
    )

    def dictify(self,obj):
        """
        Serialize a Residence object to a dict for CRUD view
        """

        appstruct=super(ResidenceCRUD,self).dictify(obj)

        if obj.location is not None:
            appstruct['address']=obj.location.street_address
            appstruct['city']=obj.location.city
            appstruct['state']=obj.location.state
            appstruct['zip']=obj.location.postal_code

        appstruct['residencetype']=obj.residencetype_id
        appstruct['parkingtype']=obj.parkingtype_id

        return appstruct

    def address(obj):
        from html import escape
        return '{address}, {city}, {state}'.format(
            address = escape(obj.location.street_address),
            city=escape(obj.location.city),
            state=escape(obj.location.state),
        ) if obj.location else None

    def url(obj):
        from html import escape

        try:
            url=escape(obj.url)
        except AttributeError:
            return ''
        else:
            return '<a href="{url}">{url}</a>'.format(url=escape(obj.url))

    url.info={'safe':True}

    list_display=[address,url]

    url_path='/residence'
