from .crud import CRUDView
from ..models import ParkingType
from colanderalchemy import SQLAlchemySchemaNode

class ResidenceCRUD(CRUDView):

    model=ParkingType
    schema=SQLAlchemySchemaNode(
        ParkingType,
        includes=['name']
    )

    list_display=['name']

    url_path='/parkingtype'
