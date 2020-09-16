from .crud import CRUDView
from ..models import ResidenceType
from colanderalchemy import SQLAlchemySchemaNode

class ResidenceTypeCRUD(CRUDView):

    model=ResidenceType
    schema=SQLAlchemySchemaNode(
        ResidenceType,
        includes=['name']
    )

    list_display=['name']

    url_path='/residencetype'
