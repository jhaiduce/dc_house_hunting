from pyramid.events import subscriber
from .crud import CRUDView, ViewDbInsertEvent,ViewDbUpdateEvent
from ..models import Residence, ListingState, WeightFactor, WeightMapping
from colanderalchemy import SQLAlchemySchemaNode
import colander
import deform
from sqlalchemy import or_, and_
from .header import view_with_header
from pyramid.view import view_config

def submit_update_score_task(success,residence_id):
    from ..tasks.scores import update_scores
    result=update_scores.delay(residence_id)

@colander.deferred
def get_parkingtype_widget(node,kw):
    from ..models import ParkingType
    dbsession=kw['request'].dbsession
    parkingtypes=dbsession.query(ParkingType)
    choices=[('','')]+[(parkingtype.id, parkingtype.name) for parkingtype in parkingtypes]
    return deform.widget.SelectWidget(values=choices)

@colander.deferred
def get_listingstate_widget(node,kw):
    from ..models import ListingState
    dbsession=kw['request'].dbsession
    listingstates=dbsession.query(ListingState)
    choices=[('','')] + \
        [(listingstate.id, listingstate.name)
         for listingstate in listingstates]
    return deform.widget.SelectWidget(values=choices)

@colander.deferred
def get_listingstate_valid(node,kw):
    from ..models import ListingState
    dbsession=kw['request'].dbsession
    listingstates=dbsession.query(ListingState)
    return colander.OneOf(
        ['default','any']+[
            str(listingstate.id) for listingstate in listingstates
        ])

@colander.deferred
def get_listingstate_filter_widget(node,kw):
    from ..models import ListingState
    dbsession=kw['request'].dbsession
    listingstates=dbsession.query(ListingState)
    choices=[('default','Default')] + [('any','Any')] + \
        [(str(listingstate.id), listingstate.name)
         for listingstate in listingstates]
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
        event.obj.listingstate_id=event.appstruct['listingstate']

        event.request.dbsession.flush()

        event.request.tm.get().addAfterCommitHook(
            submit_update_score_task,args=[event.obj.id])

def sort_label(field,label=None,current_order='desc',current_field=None):

    if current_field==field:
        # Reverse sort order
        if current_order=='desc':
            order='asc'
        elif current_order=='asc':
            order='desc'
        else:
            order='desc'
    else:
        order='desc'

    if label is None: label=field.replace("_", " ").title()

    return '<a href="?sort={}&order={}">{}</a>'.format(
        field,order,label)

def dollar_format(value):
    return '${:,.2f}'.format(value) if value is not None else '-'

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

url.info={'safe':True, 'basic_label':'URL'}

def price(obj):
    return dollar_format(obj.price)

def monthly_cost(obj):
    return dollar_format(obj.monthly_cost)

def hoa_fee(obj):
    return dollar_format(obj.hoa_fee)

hoa_fee.info={'basic_label':'HOA fee'}

def bathrooms(obj):
    if obj.bathrooms:
        if obj.half_bathrooms is not None and obj.half_bathrooms > 0:
            return '{}/{}'.format(obj.bathrooms,obj.half_bathrooms)
        else:
            return str(obj.bathrooms)
    else:
        return '-'

def bedrooms(obj):
    return obj.bedrooms if obj.bedrooms is not None else '-'

def area(obj):
    if obj.area is None:
        return '-'
    else:
        return '{:,}'.format(obj.area)

area.info={'basic_label':'Floor space (sq. ft.)'}

def score(obj):
    return '{:0.2f}'.format(obj.score) if obj.score is not None else '-'

def yesno(value):
    if value is None:
        return '-'
    elif value:
        return 'y'
    else:
        return 'n'

def seen(obj):
    return yesno(obj.seen)

sort_columns=[ 'seen','address','score','bedrooms','bathrooms',
    'area','price','hoa_fee','url','monthly_cost']

class RangeWidget(deform.widget.Widget):
    template="dc_house_hunting:templates/range.pt"
    type_name = "range"

    _pstruct_schema = colander.SchemaNode(
        colander.Mapping(),
        colander.SchemaNode(deform.widget._StrippedString(), name="min"),
        colander.SchemaNode(deform.widget._StrippedString(), name="max"),
    )

    def serialize(self, field, cstruct=None, **kw):
        if cstruct is colander.null:
            range_min = ""
            range_max = ""
        else:
            if cstruct['min'] is colander.null:
                range_min=''
            else:
                range_min = cstruct['min']

            if cstruct['max'] is colander.null:
                range_max = ''
            else:
                range_max = cstruct['max']

        kw.setdefault("range_min", range_min)
        kw.setdefault("range_max", range_max)

        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except colander.Invalid as exc:
                raise colander.Invalid(field.schema, deform.widget.text_("Invalid pstruct: %s" % exc))

            return validated

def Range(fieldtype):

    class RangeMapping(colander.MappingSchema):
        minimum=colander.SchemaNode(
            fieldtype,
            name='min',
            label='min',
            missing=None)
        maximum=colander.SchemaNode(
            fieldtype,
            name='max',
            label='max',
            missing=None)
        widget=RangeWidget()
        missing={'min':None,'max':None}

    return RangeMapping()

@colander.deferred
def get_loctype_widget(node, kw):

    loctypes = kw['request'].dbsession.query(
        LocationType).order_by(LocationType.id)
    choices=[(loctype.id,loctype.name) for loctype in loctypes]
    return deform.widget.SelectWidget(values=choices)

class FilterSchema(colander.MappingSchema):

    sort=colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        validator=colander.OneOf(sort_columns),
        missing='score')
    order=colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        validator=colander.OneOf(['asc','desc']),
        missing='desc')

    price=Range(colander.Decimal())
    monthly_cost=Range(colander.Decimal())
    score=Range(colander.Float())
    bedrooms=Range(colander.Integer())
    bathrooms=Range(colander.Integer())
    floorspace=Range(colander.Float())
    seen=colander.SchemaNode(
        colander.String(),
        widget=deform.widget.SelectWidget(
            values=[
                ('any','Any'),
                ('false','False'),
                ('true','True'),
            ]
        ),
        valid=colander.OneOf(['any','false','true']),
        missing='any'
    )
    rejected=colander.SchemaNode(
        colander.String(),
        widget=deform.widget.SelectWidget(
            values=[
                ('any','Any'),
                ('false','False'),
                ('true','True'),
            ]
        ),
        valid=colander.OneOf(['any','false','true']),
        missing='false'
    )
    listingstate=colander.SchemaNode(
        colander.String(),default='default',widget=get_listingstate_filter_widget,
        valid=get_listingstate_valid,
        title='Listing state',
        missing='default'
    )

class ResidenceCRUD(CRUDView):

    def __init__(self, request):

        super(ResidenceCRUD,self).__init__(request)

        for name in sort_columns:
            getter=globals()[name]
            info=getattr(getter,'info',{})
            info['basic_label']=info.get('basic_label',None)
            if not hasattr(getter,'sort_label_applied'):
                info['label']=sort_label(
                    name,info.get('basic_label',None),
                    request.params.get('order','desc'),
                    request.params.get('sort',None))
            getter.info=info
            getter.request=request

    list_display=[seen, address, score, bedrooms, bathrooms, area, price, hoa_fee,monthly_cost, url]

    model=Residence
    schema=SQLAlchemySchemaNode(
        Residence,
        includes=[
            'url',
            'seen',
            'rejected',
            colander.SchemaNode(
                colander.Integer(),
                name='listingstate',
                title='Listing state',
                widget=get_listingstate_widget,
                missing=None
            ),
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
            'hoa_fee',
            'insurance_',
            'taxes',
            'coop',
            'area',
            'lotsize',
            'kitchen_score',
            'bike_storage_score',
            colander.SchemaNode(
                colander.Integer(),
                name='parkingtype',
                title='Parking',
                widget=get_parkingtype_widget,
                missing=None
            ),
            'notes',
        ],
        overrides={
            'price':{
                'schema':colander.SchemaNode(
                    colander.Decimal('0.01'),
                ),
            },
            'notes':{
                'widget':deform.widget.TextAreaWidget()
            },
            'lotsize':{
                'title':'Lot size (acres)'
            },
            'area':{
                'title':'Floor space (sq. ft.)'
            },
            'hoa_fee':{
                'title':'HOA fee'
            },
            'taxes':{
                'title':'Property tax'
            },
            'insurance_':{
                'title':'Insurance'
            },
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
        appstruct['listingstate']=obj.listingstate_id

        return appstruct

    def get_list_query(self,appstruct):
        query=super(ResidenceCRUD,self).get_list_query()

        rejected=appstruct.get('rejected','false')
        if rejected == 'false':
            query=query.filter(
                or_(Residence.rejected==False, Residence.rejected==None)
            )
        elif rejected == 'true':
            query=query.filter(
                Residence.rejected==True
            )

        seen=appstruct.get('seen','any')
        if seen == 'false':
            query=query.filter(
                or_(Residence.seen==False, Residence.seen==None)
            )
        elif seen == 'true':
            query=query.filter(Residence.seen==True)

        if appstruct.get('listingstate','default')=='default':
            query=query.outerjoin(
                Residence.listingstate
            ).filter(
                # Filter out withdrawn and closed listings
                or_(
                    and_(
                        ListingState.name!='Withdrawn',
                        ListingState.name!='Closed',
                    ),
                    Residence.listingstate_id==None,
                )
            )
        elif appstruct['listingstate'] != 'any':
            try:
                listingstate_id=int(appstruct['listingstate'])
            except:
                pass
            else:
                if listingstate_id in [
                        listingstate.id
                        for listingstate in
                        self.request.dbsession.query(ListingState)]:
                    query = query.outerjoin(
                        Residence.listingstate
                    ).filter(ListingState.id == listingstate_id)

        for field in ['price','monthly_cost','score','bedrooms','bathrooms','floorspace']:
            field_mapper={
                'floorspace':Residence.area
            }

            column=field_mapper.get(field,None)

            if column is None: column=getattr(Residence,field)

            filter_range=appstruct.get(field,{'min':None,'max':None})

            if filter_range['min']:
                query=query.filter(column >= filter_range['min'])

            if filter_range['max']:
                query=query.filter(column <= filter_range['max'])

        sort_field=self.request.params.get('sort','score')
        order=self.request.params.get('order','desc')

        if sort_field not in sort_columns:
            sort_field='score'

        sort=getattr(Residence,sort_field)

        if order=='desc':
            sort=sort.desc()

        return query.order_by(sort)

    @property
    def filter_form(self):
        schema=FilterSchema().bind(request=self.request)
        return deform.Form(schema, buttons=['update filters'], method='GET')

    def _details_route(self, obj):
        """
        Get a route for the edit action based on an objects primary keys.

        :param obj: The instance of a model on which the routes values should
            be based.

        :return: A URL which can be used as the routing URL for redirects or
            displaying the URL on the page.
        """
        kw = self._get_route_pks(obj)
        return self.request.route_url('residence_details', **kw)

    @view_with_header
    def list(self):
        """
        List all items for a Model. This is the default view that can be
        overridden by subclasses to change its behavior.

        :return: A dict with a single key ``items`` that is a query which when
            iterating over yields all items to be listed.
        """

        controls=list(self.request.GET.items())

        try:
            appstruct=self.filter_form.validate(controls)
        except deform.ValidationFailure as e:
            filter_form=e.render()
            appstruct={}
        else:
            filter_form=self.filter_form.render(appstruct)

        items = self.get_list_query(appstruct)

        filter_summary=[]

        for field in ['price','monthly_cost','score','bedrooms','bathrooms','floorspace']:
            range_filter=appstruct.get(field,{'min':None,'max':None})

            if range_filter['min'] or range_filter['max']:
                filter_summary.append(
                    '{name}: {range_min} - {range_max}'.format(
                        name=field.replace('_',' ').capitalize(),
                        range_min=range_filter['min'] or '',
                        range_max=range_filter['max'] or ''
                    ))

        if appstruct.get('seen','any')!='any':
            if appstruct['seen']=='true':
                filter_summary.append('Seen: y')
            if appstruct['seen']=='false':
                filter_summary.append('Seen: n')

        if appstruct.get('rejected','any')!='any':
            if appstruct['rejected']=='true':
                filter_summary.append('Rejected: y')
            if appstruct['rejected']=='false':
                filter_summary.append('Rejected: n')

        if appstruct.get('listingstate','default')!='any':
            if appstruct.get('listingstate','default')=='default':
                filter_summary.append('Listing state: Not closed or withdrawn')
            else:
                try:
                    listingstate_id=int(appstruct['listingstate'])
                except:
                    pass
                else:
                    filter_summary.append('Listing state: {}'.format(
                        self.request.dbsession.query(ListingState).filter(
                            ListingState.id==listingstate_id).one().name
                    ))

        retparams = {
            'items': items,
            'filter_form': filter_form,
            'filter_summary': ', '.join(filter_summary)
        }

        return retparams

    url_path='/residence'

class ResidenceViews(object):
    def __init__(self, request):
        self.request = request

    @view_with_header
    @view_config(route_name='residence_details', renderer='../templates/residence_details.jinja2')
    def details(self):
        """
        Display details for a Residence
        """

        residence_id=int(self.request.matchdict['id'])

        dbsession=self.request.dbsession

        residence=dbsession.query(Residence).filter(Residence.id==residence_id).one()

        weights={
            field:WeightFactor.get(field,dbsession).weight
            for field in residence.score_fields
        }

        scores={
            field:residence.get_score_component(field,weighted=False)
            for field in residence.score_fields
        }

        return dict(residence=residence,dollar_format=dollar_format,weights=weights,scores=scores,sum=sum)
