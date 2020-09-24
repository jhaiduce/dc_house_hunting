from .crud import CRUDView
from ..models import ParkingType
from colanderalchemy import SQLAlchemySchemaNode

class ParkingTypeCRUD(CRUDView):

    model=ParkingType
    schema=SQLAlchemySchemaNode(
        ParkingType,
        includes=['name','score']
    )

    list_display=['name','score']

    url_path='/parkingtype'
