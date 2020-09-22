from ..models.housing_search_models import Residence
from ..celery import celery

from celery.utils.log import get_task_logger

import transaction

logger = get_task_logger(__name__)

@celery.task(ignore_result=False)
def update_scores():

    from ..celery import session_factory
    from ..models import get_tm_session

    dbsession=get_tm_session(session_factory, transaction.manager)

    logger.debug('Received update_scores task')

    for residence in dbsession.query(Residence):
        residence.compute_score()

    transaction.commit()
