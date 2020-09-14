from .crud import CRUDView, ViewDbInsertEvent,ViewDbUpdateEvent
from ..models import Residence
from colanderalchemy import SQLAlchemySchemaNode
import colander
import deform

class ResidenceCRUD(CRUDView):

    model=Residence
    schema=SQLAlchemySchemaNode(
        Residence,
        includes=[
            colander.SchemaNode(
                colander.String(),
                name='address'),
            colander.SchemaNode(
                colander.Integer(),
                name='residencetype',
                title='Residence type',
                widget=deform.widget.SelectWidget()
            ),
            'bedrooms',
            'bathrooms',
            'laundry',
            'basement',
            'attic',
            'price',
            colander.SchemaNode(
                colander.Integer(),
                name='parkingtype',
                title='Parking',
                widget=deform.widget.SelectWidget()
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
            }
        }
    )

    url_path='/residence'
